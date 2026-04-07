from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    goals: Optional[str] = None
    context: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[str] = None
    context: Optional[str] = None


class WorkspaceOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    goals: Optional[str] = None
    context: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
