from pydantic import BaseModel, Field


class CreateMessageRequest(BaseModel):
    role: str = Field(
        min_length=1,
        max_length=20,
    )
    content: str = Field(
        min_length=1,
        max_length=20_000,
    )


class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: str