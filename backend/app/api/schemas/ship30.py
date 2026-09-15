from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class Ship30Request(BaseModel):
    topic: str = Field(..., min_length=2, description="Topic or prompt for the Ship30 essay")


class Ship30Response(BaseModel):
    content: str
    sources: List[Dict[str, Any]]
    grounded: bool
