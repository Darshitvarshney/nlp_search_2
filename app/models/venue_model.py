# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime


# class Media(BaseModel):
#     url: Optional[str] = None
#     public_id: Optional[str] = None


# class VenueLocation(BaseModel):
#     locality: str
#     fullAddress: str
#     city: Optional[str] = None
#     state: Optional[str] = None
#     country: Optional[str] = None
#     googleMapsLink: Optional[str] = None
#     pincode: str


# class VenuePackage(BaseModel):
#     id: Optional[str] = Field(default=None, alias="_id")

#     # CORE
#     title: str
#     description: Optional[str] = None
#     startingPrice: int

#     # LOCATION (CRITICAL FOR SEARCH)
#     location: VenueLocation

#     # MEDIA
#     featuredImage: Optional[Media] = None

#     # ADMIN / FILTERING
#     approved: bool = False
#     visibility: str = "public"
#     isPremium: bool = False
#     inquiryCount: int = 0

#     # TIMESTAMPS
#     createdAt: Optional[datetime] = None
#     updatedAt: Optional[datetime] = None

#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True
from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, DictField


class VenuePackage(Document):
    meta = {"collection": "venuepackages"}  # change to your real collection

    title = StringField(required=True)
    description = StringField()
    startingPrice = IntField()

    # Store nested location as dict (matches your DB JSON)
    location = DictField()

    approved = BooleanField(default=False)
    visibility = StringField(default="public")
    isPremium = BooleanField(default=False)
    inquiryCount = IntField(default=0)

    createdAt = DateTimeField()
    updatedAt = DateTimeField()
