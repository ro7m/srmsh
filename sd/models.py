
from pydantic import BaseModel
from typing import Optional

class IdentityRecord(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        # Allow extra fields but ignore them
        extra = "ignore"

class SimilarityResult(BaseModel):
    similarity_score: float
    is_same_person: bool
    method: str
    confidence: float = 1.0
    details: Optional[dict] = None
