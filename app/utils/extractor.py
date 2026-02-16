import re


GEO_KEYWORDS = [
    "near",
    "in",
    "at",
    "around",
    "pincode",
    "pin",
    "area",
    "location"
]

def extract_pincode(query: str):
    """
    Context-aware Indian pincode extraction.
    Prevents conflict with budget numbers like 200000.
    """

    # Step 1: Find all 6-digit numbers
    matches = re.findall(r"\b\d{6}\b", query)

    if not matches:
        return None

    # Step 2: Check context around the number
    for match in matches:
        idx = query.find(match)
        context_window = query[max(0, idx - 20): idx].lower()

        if any(keyword in context_window for keyword in GEO_KEYWORDS):
            return match

    return None
# Budget normalization (k, lakh, cr)
def normalize_budget(value: int, unit: str | None) -> int:
    if not unit:
        return value

    unit = unit.lower()

    if unit in ["k", "thousand"]:
        return value * 1000
    if unit in ["lakh", "lac"]:
        return value * 100000
    if unit in ["cr", "crore"]:
        return value * 10000000

    return value


# Extract Budget (under, below, max, upto)
def extract_budget(query: str):
    """
    Extract only MAX budget for hard DB filtering.
    Examples:
    - under 50k
    - below 2 lakh
    - max 50000
    - budget 1 lakh
    """
    patterns = [
        r"(under|below|max|upto)\s*(\d+)\s*(k|lakh|lac|cr|crore)?",
        r"budget\s*(\d+)\s*(k|lakh|lac|cr|crore)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            value = int(match.group(2))
            unit = match.group(3)
            return normalize_budget(value, unit)

    return None



def extract_experience(query: str):
    """
    Crash-proof experience extractor.
    Never throws ValueError.
    """

    if not query:
        return None

    query = query.lower()

    # Direct numeric + experience patterns
    patterns = [
        r"(\d+)\s*\+\s*(?:years?|yrs?)",
        r"more than\s*(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*(?:years?|yrs?)\s*(?:experience|exp)",
        r"experience\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*(?:years?|yrs?)\s*of\s*experience",
        r"(\d+)\s*year\s*experience",
        r"experience\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue  # never crash pipeline

    return None




# HARD FILTER: Extract Working Since (year-based filtering)
def extract_working_since(query: str):
    """
    Extract working since year for HARD filtering.
    Covers real-world phrasing.
    """
    patterns = [
        r"working since\s*(19|20)\d{2}",
        r"since\s*(19|20)\d{2}",
        r"from\s*(19|20)\d{2}",
        r"in\s*market\s*since\s*(19|20)\d{2}",
        r"established\s*in\s*(19|20)\d{2}",
        r"since year\s*(19|20)\d{2}",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            year = re.search(r"(19|20)\d{2}", match.group(0))
            if year:
                return int(year.group(0))

    return None



# MAIN HARD FILTER EXTRACTOR 
def extract_hard_filters(query: str) -> dict:
    """
    STRICT HARD FILTER extractor.
    ONLY extracts fields used in DB-level filtering.

    Does NOT extract:
    - city
    - state
    - locality
    - pincode
    - semantic tags
    - anything soft

    Architecture aligned:
    HARD FILTER → DB
    SOFT SEARCH → Ranking layer
    """
    if not query:
        return {
            "min_experience": None,
            "budget_max": None,
            "working_since": None,
        }

    query_lower = query.lower()

    hard_filters = {
        "min_experience": extract_experience(query_lower),
        "budget_max": extract_budget(query_lower),
        "working_since": extract_working_since(query_lower),
        "pincode": extract_pincode(query_lower),  
    }


    return hard_filters
