from typing import List, Dict, Any


def paginate_results(
    results: List[Dict[str, Any]],
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Pagination applied AFTER ranking (final layer).

    Why AFTER ranking?
    - Ensures top relevant results fill early pages
    - Fixes geo-priority issue (e.g., Ghaziabad first pages)

    Args:
        results: Ranked list of results
        page: Page number (1-based)
        limit: Items per page

    Returns:
        {
            "data": paginated_results,
            "pagination": {
                "page": int,
                "limit": int,
                "total_results": int,
                "total_pages": int,
                "has_next": bool,
                "has_prev": bool
            }
        }
    """

    # Safety clamps (API protection)
    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    if limit > 50:  # hard cap to prevent abuse
        limit = 50

    total_results = len(results)

    # If no results
    if total_results == 0:
        return {
            "data": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_results": 0,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False,
            },
        }

    # Calculate slicing indexes
    start = (page - 1) * limit
    end = start + limit

    paginated_data = results[start:end]

    # Calculate total pages (ceil division)
    total_pages = (total_results + limit - 1) // limit

    return {
        "data": paginated_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_results": total_results,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
