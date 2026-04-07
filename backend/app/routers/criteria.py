from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.criteria import Criterion, DecisionCriterionWeight
from app.schemas.criteria import CriterionOut, WeightsUpdate, WeightOut
from app.core.deps import get_current_user

router = APIRouter(tags=["Criteria"])


@router.get("/criteria", response_model=List[CriterionOut])
def list_criteria(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Criterion).all()


@router.get("/decisions/{decision_id}/weights", response_model=List[WeightOut])
def get_weights(decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    weights = db.query(DecisionCriterionWeight).filter(
        DecisionCriterionWeight.decision_id == decision_id
    ).all()
    result = []
    for w in weights:
        result.append(WeightOut(
            id=w.id, decision_id=w.decision_id, criterion_id=w.criterion_id,
            criterion_name=w.criterion.name, weight=w.weight
        ))
    return result


@router.put("/decisions/{decision_id}/weights", response_model=List[WeightOut])
def set_weights(
    decision_id: int, payload: WeightsUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Delete existing weights and replace
    db.query(DecisionCriterionWeight).filter(
        DecisionCriterionWeight.decision_id == decision_id
    ).delete()

    result = []
    for item in payload.weights:
        crit = db.query(Criterion).filter(Criterion.id == item.criterion_id).first()
        if not crit:
            raise HTTPException(status_code=404, detail=f"Criterion {item.criterion_id} not found")
        w = DecisionCriterionWeight(
            decision_id=decision_id, criterion_id=item.criterion_id, weight=item.weight
        )
        db.add(w)
        db.flush()
        result.append(WeightOut(
            id=w.id, decision_id=w.decision_id, criterion_id=w.criterion_id,
            criterion_name=crit.name, weight=w.weight
        ))
    db.commit()
    return result
