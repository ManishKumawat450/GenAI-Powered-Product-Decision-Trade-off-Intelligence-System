from pydantic import BaseModel
from typing import Optional, List


class CriterionOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_global: bool

    model_config = {"from_attributes": True}


class WeightItem(BaseModel):
    criterion_id: int
    weight: float


class WeightsUpdate(BaseModel):
    weights: List[WeightItem]


class WeightOut(BaseModel):
    id: int
    decision_id: int
    criterion_id: int
    criterion_name: str
    weight: float

    model_config = {"from_attributes": True}
