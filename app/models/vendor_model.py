# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime


# class Media(BaseModel):
#     url: Optional[str] = None
#     public_id: Optional[str] = None


# class Wallet(BaseModel):
#     balance: int = 0
#     transactions: List[str] = []


# class Vendor(BaseModel):
#     id: Optional[str] = Field(default=None, alias="_id")

#     # BASIC
#     vendorName: str
#     experience: int
#     teamSize: Optional[int] = None
#     workingSince: int

#     # LOCATION
#     state: str
#     city: str
#     locality: str
#     address: Optional[str] = None
#     pincode: Optional[str] = None

#     # MEDIA
#     profile: Optional[Media] = None
#     coverImage: Optional[Media] = None

#     # ADMIN / SEARCH CRITICAL
#     status: str = "pending"
#     featured: bool = False
#     verifiedBadge: bool = False
#     role: str = "vendor"

#     # ACTIVITY (VERY IMPORTANT FOR SORTING)
#     lastActive: Optional[datetime] = None
#     createdAt: Optional[datetime] = None
#     updatedAt: Optional[datetime] = None

#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True
from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField


class Vendor(Document):
    meta = {"collection": "vendors"}  # change to your actual collection name

    # BASIC
    vendorName = StringField(required=True)
    experience = IntField()
    teamSize = IntField()
    workingSince = IntField()

    # LOCATION
    state = StringField()
    city = StringField()
    locality = StringField()
    address = StringField()
    pincode = StringField()

    # ADMIN / SEARCH
    status = StringField(default="pending")
    featured = BooleanField(default=False)
    verifiedBadge = BooleanField(default=False)
    role = StringField(default="vendor")

    # ACTIVITY
    lastActive = DateTimeField()
    createdAt = DateTimeField()
    updatedAt = DateTimeField()
