from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class CommentCreate(BaseModel):
    content: str
    option_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    decision_id: int
    option_id: Optional[int] = None
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[Any] = None
    timestamp: datetime

    model_config = {"from_attributes": True}
