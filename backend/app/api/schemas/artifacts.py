from pydantic import BaseModel, Field
from typing import Optional


class CreateArtifactRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: str = Field("markdown", description="Artifact type: 'markdown' or 'html'")
    content: Optional[str] = Field(None, description="Optional custom content or prompt context")


class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    title: str
    type: str
    content: str
    created_at: str
