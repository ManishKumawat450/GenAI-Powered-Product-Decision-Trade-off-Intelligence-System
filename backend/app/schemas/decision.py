from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ConstraintCreate(BaseModel):
    type: str
    description: str
    value: Optional[str] = None


class ConstraintUpdate(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None


class ConstraintOut(BaseModel):
    id: int
    decision_id: int
    type: str
    description: str
    value: Optional[str] = None

    model_config = {"from_attributes": True}


class OptionCreate(BaseModel):
    label: str
    name: str
    description: Optional[str] = None
    order: int = 0


class OptionUpdate(BaseModel):
    label: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class OptionOut(BaseModel):
    id: int
    decision_id: int
    label: str
    name: str
    description: Optional[str] = None
    order: int

    model_config = {"from_attributes": True}


class DecisionCreate(BaseModel):
    title: str
    problem_statement: Optional[str] = None
    success_metrics: Optional[str] = None


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    success_metrics: Optional[str] = None
    status: Optional[str] = None


class DecisionOut(BaseModel):
    id: int
    workspace_id: int
    title: str
    problem_statement: Optional[str] = None
    success_metrics: Optional[str] = None
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DecisionVersionOut(BaseModel):
    id: int
    decision_id: int
    version_number: int
    snapshot: Optional[Any] = None
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
