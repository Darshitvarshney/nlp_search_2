import os
from app.utils.extractor import extract_hard_filters
from app.utils.llm import enrich_with_llm  # your existing LLM utility


def is_llm_enabled() -> bool:
    return os.getenv("ENABLE_LLM", "false").lower() == "true"


async def run_nlp_engine(query: str, flag: str) -> dict:

    if not query:
        return {
            "raw_query": "",
            "entity_name": None,
            "flag": flag,
            # HARD FILTERS
            "min_experience": None,
            "budget_max": None,
            "working_since": None,
            # SOFT FIELDS (to be enriched by LLM later)
            "city": None,
            "state": None,
            "locality": None,
            "pincode": None,
            "semantic_tags": []
        }

    # HARD FILTER EXTRACTION ONLY (NO GEO)
    hard_filters = extract_hard_filters(query)

    # Base structured query (minimal, clean)
    structured_query = {
        "raw_query": query,
        "entity_name": None,
        "flag": flag,

        # HARD FILTERS (for hardfilter.py / DB query)
        "min_experience": hard_filters.get("min_experience"),
        "budget_max": hard_filters.get("budget_max"),
        "working_since": hard_filters.get("working_since"),

        # DO NOT TOUCH GEO HERE (as per your instruction)
        "city": None,
        "state": None,
        "locality": None,
        "pincode": hard_filters.get("pincode"),


        # For soft ranking later
        "semantic_tags": []
    }
    # print("Structured Query after HARD filter extraction:", structured_query)
    # LLM ENRICHMENT (NOW GEO CAN BE ADDED)
    if is_llm_enabled():
        try:
            enriched_data = await enrich_with_llm(
                query=query,
                extracted_filters=structured_query
            )
            # print(f" LLM Enrichment Output: {enriched_data}")
            if enriched_data:
                # Safe merge: LLM enriches, but DOES NOT override hard filters
                for key, value in enriched_data.items():
                    if value is None:
                        continue

                    structured_query[key] = value


        except Exception as e:
            print("LLM FAILED → Continuing with HARD FILTER ONLY:", str(e))
    else:
        print("LLM DISABLED → Using HARD FILTER EXTRACTION ONLY")
   
    flag_lower = (flag or "").lower()

    if flag_lower == "vendor":
        structured_query["intent"] = "vendor_search"
    elif flag_lower == "venue":
        structured_query["intent"] = "venue_search"
    else:
        structured_query["intent"] = "hybrid_search"

    return structured_query
