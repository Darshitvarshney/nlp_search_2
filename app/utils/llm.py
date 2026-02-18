import os
import json
from typing import Dict, Any, Optional

from openai import AsyncOpenAI


def get_openai_client() -> Optional[AsyncOpenAI]:
    """
    Lazy client initialization to prevent startup crashes
    if OPENAI_API_KEY is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("OPENAI_API_KEY not found. LLM enrichment disabled.")
        return None

    return AsyncOpenAI(api_key=api_key)


def _build_prompt(query: str, extracted_filters: Dict[str, Any]) -> str:
    return f"""
You are an AI search enrichment engine for a wedding marketplace (vendors & venues).

USER QUERY:
"{query}"

REGEX-EXTRACTED FILTERS 
{json.dumps(extracted_filters, indent=2)}

YOUR TASK:
1. Verify regex extractor (like budget, experience, working_since, pincode) and if regex extractor have filled wrong values then correct them or is missed them. For example, if regex extracted working since from query as it may in different form like in market from 2000 then extract it.
2. Enrich  missing fields (city, state, locality, semantic_tags) and if city,state are not present  in the query then fill them with null instead of wrong extraction.
GEO EXTRACTION PRIORITY:
3. Extract explicit geographic entities from the query text

CRITICAL AUTOCORRECTION RULES:
- Correct misspelled entity names (e.g., "Biteh" → "Bite")
- Correct city/state spelling mistakes 
- DO NOT hallucinate new names
- Only correct if the intent is clear
- Preserve original meaning strictly
- If unsure, keep original value (do NOT guess)
IMPORTANT EXTRACTION RULES:
- If a known city name appears → fill "city"
- If a known state name appears → fill "state"
- If both city and state appear → extract BOTH
- extract enity name if mentioned in the query 
-if term in query is matching with any of the city , state ,locality then extract it as entity name
- Do NOT ignore clear geo text like: "meerut", "uttar pradesh", "noida", etc.
- Pincode (6-digit) = highest geo priority
- Locality examples: NH2, Sector 62, MG Road, Raj Nagar
- 
locality > city > state

EXAMPLES:
Query: "vendors in meerut uttar pradesh"
→ city = "Meerut", state = "Uttar Pradesh"

Query: "vendor in 245368"
→ pincode = "245368"

Query: "vendors in NH2"
→ locality = "NH2"

OUTPUT STRICT JSON FORMAT:
{{
    "raw_query": "{query}",
    "entity_name": null,
    "min_experience": number or null,
    "budget_max": number or null,
    "working_since": number or null,
    "city": string or null,
    "state": string or null,
    "locality": string or null,
    "pincode": string or null,
    "entity_name": string or null,
    "semantic_tags": [string]

}}

RETURN ONLY VALID JSON.
NO EXPLANATION.
"""



async def enrich_with_llm(query: str, extracted_filters: Dict[str, Any]) -> Dict[str, Any]:
    try:
        client = get_openai_client()

        # CRITICAL: Safe fallback if no API key
        if client is None:
            return {
                "entity_name": None,
                "category": None,
                "style": None,
                "semantic_tags": [],
                "confidence": 0.0,
            }

        prompt = _build_prompt(query, extracted_filters)
        # print(f"🔍 LLM Prompt:\n{prompt}")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict JSON generator for NLP search enrichment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        # print(f"LLM Enrichment Output: {parsed}")
        # print(f"LLM Enrichment Output (raw): {content}")
        return {
            "raw_query": parsed.get("raw_query"),
            "flag": parsed.get("flag"),
            "city": parsed.get("city"),
            "state": parsed.get("state"),
            "locality": parsed.get("locality"),
            "pincode": parsed.get("pincode"),
            "min_experience": parsed.get("min_experience"),
            "budget_max": parsed.get("budget_max"),
            "working_since": parsed.get("working_since"),
            "entity_name": parsed.get("entity_name"),
            "category": parsed.get("category"),
            "style": parsed.get("style"),
            "semantic_tags": parsed.get("semantic_tags", []),
            "confidence": parsed.get("confidence", 0.5),
        }
    except Exception as e:
        print("LLM ENRICHMENT FAILED:", str(e))
        return {
            "entity_name": None,
            "category": None,
            "style": None,
            "semantic_tags": [],
            "confidence": 0.0,
        }