from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    query: str = Field(..., description="User search query")
    flag: str = Field(..., description="vendor | venue | all")
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=10, ge=1, le=50)
   
    threshold_ratio: Optional[float] = Field(default=0.20)