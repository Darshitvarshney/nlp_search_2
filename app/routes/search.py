import time
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime

from app.models.request import SearchRequest
from app.utils.nlp_engine import run_nlp_engine
from app.utils.hard_filter import hard_filter_vendors, hard_filter_venues
    

router = APIRouter()

@router.get("/db-health")
def db_health():
    return {"status": "Connection is healthy"}


from app.utils.pagination import paginate_results
from app.utils.ranker import  apply_strict_filter, rank_results


@router.post("/search")
async def search_api(payload: SearchRequest):
    start_time = time.time()

    # Prevent empty or meaningless queries
    if not payload.query or not payload.query.strip():
        return JSONResponse(
            content={
                "structured_query": {
                    "raw_query": "",
                    "message": "Empty search query. Please provide search keywords."
                },
                "vendors": [],
                "venues": [],
                "pagination": {
                    "page": payload.page,
                    "limit": payload.limit,
                    "total_vendor_results": 0,
                    "total_venue_results": 0,
                    "total_pages_vendors": 0,
                    "total_pages_venues": 0,
                },
                "execution_time_ms": 0,
            }
        )
   
    structured_query = await run_nlp_engine(
        query=payload.query,
        flag=payload.flag
    )
    print("Structured Query after NLP Engine:", structured_query)
    # print("Structured Query:", structured_query)
    page = payload.page
    limit = payload.limit

    vendors = []
    venues = []

    intent = structured_query.get("intent", "hybrid_search")
    
    # HARD FILTER (DB via models)
    if intent == "vendor_search":
        vendors = await hard_filter_vendors(structured_query)
        

    elif intent == "venue_search":
        venues = await hard_filter_venues(structured_query)

    else:  # hybrid
        # hard search as insufficient data is available for venues, we will return empty results for venues if budget_max is provided in the query.
        # if structured_query.get("budget_max") :
        #     vendors = []
        #     venues = await hard_filter_venues(structured_query)
        # else :
        #     vendors = await hard_filter_vendors(structured_query)
        #     venues = []
        vendors = await hard_filter_vendors(structured_query)
        venues = await hard_filter_venues(structured_query)
    # SOFT RANKING (Relevance Layer)
    if vendors:

        vendors = rank_results(vendors, structured_query)
       
        vendors = apply_strict_filter(vendors, threshold_ratio=payload.threshold_ratio)
        
        
    if venues:
        print(structured_query)
        venues = rank_results(venues, structured_query)
      
        venues = apply_strict_filter(venues,threshold_ratio=payload.threshold_ratio)
  

    #  FINAL PAGINATION (AFTER RANKING)
    paginated_vendors = paginate_results(vendors, page, limit)
    paginated_venues = paginate_results(venues, page, limit)

    execution_time = (time.time() - start_time) * 1000

    response_data = {
        "structured_query": structured_query,
        "vendors": paginated_vendors["data"],
        "venues": paginated_venues["data"],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_vendor_results": paginated_vendors["pagination"]["total_results"],
            "total_venue_results": paginated_venues["pagination"]["total_results"],
            "total_pages_vendors": paginated_vendors["pagination"]["total_pages"],
            "total_pages_venues": paginated_venues["pagination"]["total_pages"],
        },
        "execution_time_ms": round(execution_time, 2),
    }
    return JSONResponse(content=jsonable_encoder(response_data))
