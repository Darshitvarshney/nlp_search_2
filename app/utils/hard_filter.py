from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId
import re
from app.models.vendor_model import Vendor
from app.models.venue_model import VenuePackage


def safe_str(value):
    """
    Convert Mongo ObjectId / non-serializable values to string safely.
    Prevents FastAPI JSON serialization crashes.
    """
    if isinstance(value, ObjectId):
        return str(value)
    return value


def safe_datetime(dt):
    """
    Convert datetime to ISO string safely.
    """
    if dt:
        try:
            return dt.isoformat()
        except Exception:
            return str(dt)
    return None


# HARD FILTER FOR VENDORS (DB → Clean Dicts)
async def hard_filter_vendors(structured_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        filters = {
            # "status": "active"  # business rule: exclude pending vendors
        }


        min_experience = structured_query.get("min_experience")
        working_since = structured_query.get("working_since")
        city = structured_query.get("city")
        state = structured_query.get("state")
        pincode = structured_query.get("pincode")
        entity_name = structured_query.get("entity_name")
        
        # FORCE TYPE CAST (CRITICAL FIX)
        
        if min_experience is not None:
            min_experience = int(min_experience)
            filters["experience__gte"] = min_experience
        

        if working_since is not None:
            working_since = int(working_since)  
            filters["workingSince__lte"] = working_since

        if entity_name:
            filters["vendorName__icontains"] = entity_name
         
        if pincode:
            filters["pincode"] = str(pincode)


        if working_since is None and min_experience is None and entity_name is None and pincode is None :  
            if state:
                filters["state__iexact"] = state
            elif city:
                filters["city__iexact"] = city  


        queryset = (
            Vendor.objects(**filters)
            .only(
                "id",
                "vendorName",
                "experience",
                "teamSize",
                "workingSince",
                "state",
                "city",
                "locality",
                "pincode",
                "lastActive",
                "createdAt",
            )
            # .order_by("-lastActive")
            .limit(200)
        )

        results: List[Dict[str, Any]] = []

        for vendor in queryset:
            results.append({
                "_id": str(vendor.id),
                "vendorName": getattr(vendor, "vendorName", None),
                "experience": getattr(vendor, "experience", None),
                "teamSize": getattr(vendor, "teamSize", None),
                "workingSince": getattr(vendor, "workingSince", None),

                #  SAFE STRING CONVERSION (avoid ObjectId issues)
                "state": safe_str(getattr(vendor, "state", None)),
                "city": safe_str(getattr(vendor, "city", None)),
                "locality": safe_str(getattr(vendor, "locality", None)),
                "pincode": safe_str(getattr(vendor, "pincode", None)), 

                # DATETIME SAFE
                "lastActive": safe_datetime(getattr(vendor, "lastActive", None)),
                "createdAt": safe_datetime(getattr(vendor, "createdAt", None)),
            })

        return results

    except Exception as e:
        print("HARD FILTER VENDOR ERROR:", str(e))
        return []


# HARD FILTER FOR VENUES
async def hard_filter_venues(structured_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        filters = {
            "visibility": "public"
            # NOTE: Do NOT force approved=True unless all DB docs are approved
        }

        budget_max = structured_query.get("budget_max")

        # provide a hard search on budget as no other field is available for venues.
        if budget_max is not  None:
            filters["startingPrice__lte"] = budget_max


        city = structured_query.get("city")
        state = structured_query.get("state")
        pincode = structured_query.get("pincode")
        entity_name = structured_query.get("entity_name")
    
        if entity_name:
            filters["title__icontains"] = entity_name


        #  ########     FOR FUTURE ENCHANCEMENT
        # if pincode:
        #     filters["pincode"] = str(pincode)


        # if budget_max is None and entity_name is None and pincode is None :  
        #     if state:
        #         filters["state__iexact"] = state
        #     elif city:
        #         filters["city__iexact"] = city  

        # Candidate Pool Query (Optimized Projection)

        queryset = (
            VenuePackage.objects(**filters)
            .only(
                "id",
                "title",
                "startingPrice",
                "location",
                "approved",
                "createdAt",
                "updatedAt",
                "isPremium",
                "inquiryCount",
            )
            # .order_by("-createdAt")
            .limit(200)
        )

        results: List[Dict[str, Any]] = []

        for venue in queryset:
            location = getattr(venue, "location", {}) or {}

            # Your DB stores ObjectId in city/state → must sanitize
            locality = safe_str(location.get("locality"))
            city = safe_str(location.get("city"))
            state = safe_str(location.get("state"))
            pincode = safe_str(location.get("pincode"))

            results.append({
                "_id": str(venue.id),

                #  IMPORTANT: ranker expects venueName
                "venueName": getattr(venue, "title", None),

                "startingPrice": getattr(venue, "startingPrice", None),
                "approved": getattr(venue, "approved", False),
                "isPremium": getattr(venue, "isPremium", False),
                "inquiryCount": getattr(venue, "inquiryCount", 0),

                #  FLATTENED GEO FIELDS (for ranking engine)
                "locality": locality,
                "city": city,
                "state": state,
                "pincode": pincode,

                # NESTED LOCATION (UI compatible)
                "location": {
                    "locality": locality,
                    "city": city,
                    "state": state,
                    "pincode": pincode,
                },

                #SAFE DATETIME (prevents JSON crash)
                "createdAt": safe_datetime(getattr(venue, "createdAt", None)),
                "updatedAt": safe_datetime(getattr(venue, "updatedAt", None)),
            })

        return results

    except Exception as e:
        print("HARD FILTER VENUE ERROR:", str(e))
        return []
