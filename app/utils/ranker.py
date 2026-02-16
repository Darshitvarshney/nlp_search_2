
from typing import List, Dict, Any
def apply_strict_filter(
    results: List[Dict[str, Any]],
    threshold_ratio
) -> List[Dict[str, Any]]:
  

    positive_scores = [
        r.get("_score", 0)
        for r in results
        if r.get("_score", 0) > 0
    ]

    if not positive_scores:
        return []

    top_score = max(positive_scores)

    
    # top_score = results[0].get("_score", 0)

    # if top_score <= 0:
    #     return []  

    threshold_score = top_score * threshold_ratio

    filtered_results = [
        r for r in results
        if r.get("_score", 0) >= threshold_score
    ]

    # Safety fallback (never return empty due to strict)
    if not filtered_results:
        return results[:5]  # keep top 5 at least

    return filtered_results




def compute_score(
    item: Dict[str, Any],
    structured_query: Dict[str, Any]
) -> int:
    """
    PURE RANKING LOGIC (LLM-AWARE)

    Priority:
    1. Entity name (exact intent)
    2. Pincode (strong geo)
    3. Locality (precise geo)
    4. City (soft geo)
    5. State (broad geo)
    6. Semantic tags
    7. Token fallback (lowest)
    """

    score = 0

    # DB fields
    name = str(item.get("vendorName") or item.get("venueName") or "").lower()
    city = str(item.get("city", "")).lower()
    state = str(item.get("state", "")).lower()
    locality = str(item.get("locality", "")).lower()
    pincode = str(item.get("pincode", "")).lower()
    experience = item.get("experience", None)
    working_since = item.get("workingSince", None)
    budget_max = item.get("startingPrice", None)
    # Handle venue nested location
    location = item.get("location")
    if isinstance(location, dict):
        locality = str(location.get("locality", locality)).lower()
        pincode = str(location.get("pincode", pincode)).lower()

    # LLM ENRICHED FIELDS (PRIMARY SIGNAL)

    q_city = str(structured_query.get("city") or "").lower()
    q_state = str(structured_query.get("state") or "").lower()
    q_locality = str(structured_query.get("locality") or "").lower()
    q_pincode = str(structured_query.get("pincode") or "").lower()
    q_entity = str(structured_query.get("entity_name") or "").lower()
    q_tags = structured_query.get("semantic_tags", [])
    q_experience = structured_query.get("min_experience")
    q_working_since = structured_query.get("working_since")
    q_budget_max = structured_query.get("budget_max")

    #  ENTITY MATCH (Highest Intent)
    if q_entity:
        if q_entity in name:
            score += 100
        # if q_entity in locality:
        #     score += 110

    # PINCODE MATCH (Strongest Geo Signal)
    if q_pincode and pincode == q_pincode:
        score += 100

    # LOCALITY MATCH (Precise Geo)
    if q_locality:
        if q_locality in locality:
            score += 50
        # if q_locality in name:
        #     score += 40
    #  CITY MATCH (Soft Geo Filter)
    if q_city and q_city == city:
        score += 50

    #  STATE MATCH (Broad Geo)
    if q_state and q_state == state:
        score += 50
    if q_experience is not None and experience is not None and experience >= q_experience:
        score+=10
    if q_working_since is not None and working_since is not None and working_since <= q_working_since:
        score+=10
    if q_budget_max is not None and budget_max is not None and budget_max <= q_budget_max:
        score+=10
    
    # SEMANTIC TAG MATCH (LLM intelligence)
    for tag in q_tags:
        tag = str(tag).lower()
        if tag in name:
            score += 15
        if tag in locality:
            score += 13

    # if score == 0:
    #     score = 1 

    return score


def rank_results(
    results: List[Dict[str, Any]],
    structured_query: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    FINAL SOFT RANKING LAYER
    - Uses LLM enriched structured_query
    - Ranker does NOT perform NLP
    """

    if not results:
        return []

    # raw_query = structured_query.get("raw_query", "")
    # tokens = tokenize_query(raw_query)

    for item in results:
        # score = compute_score(item, tokens, structured_query)
        score = compute_score(item, structured_query)
        item["_score"] = score  

    # Sort by relevance score + recency fallback
    ranked = sorted(
        results,
        key=lambda x: (
            x.get("_score", 0),
            x.get("lastActive", "")
        ),
        reverse=True
    )

    return ranked