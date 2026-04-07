from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class OptionCriterionScore(BaseModel):
    criterion_id: int
    criterion_name: str
    raw_score: float
    weighted_score: float
    explanation: str


class OptionRankingOut(BaseModel):
    option_id: int
    option_label: str
    option_name: str
    rank: int
    total_score: float
    scores: List[OptionCriterionScore]
    risks: List[str]
    recommendations: List[str]


class TradeOffCell(BaseModel):
    option_name: str
    scores: dict


class EvaluateResponse(BaseModel):
    decision_id: int
    reasoning_output_id: int
    rankings: List[OptionRankingOut]
    narrative: str
    trade_off_matrix: List[dict]
    is_llm_assisted: bool = False
    created_at: datetime


class PrioritizeRequest(BaseModel):
    decision_ids: List[int]


class PrioritizeItem(BaseModel):
    decision_id: int
    decision_title: str
    rank: int
    total_score: float
    impact: float
    effort: float
    summary: str


class PrioritizeResponse(BaseModel):
    items: List[PrioritizeItem]
