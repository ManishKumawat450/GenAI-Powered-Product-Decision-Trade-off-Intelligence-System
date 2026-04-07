from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.decision import Constraint
from app.schemas.decision import ConstraintCreate, ConstraintUpdate, ConstraintOut
from app.core.deps import get_current_user

router = APIRouter(tags=["Constraints"])


@router.get("/decisions/{decision_id}/constraints", response_model=List[ConstraintOut])
def list_constraints(decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Constraint).filter(Constraint.decision_id == decision_id).all()


@router.post("/decisions/{decision_id}/constraints", response_model=ConstraintOut, status_code=201)
def create_constraint(
    decision_id: int, payload: ConstraintCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = Constraint(**payload.model_dump(), decision_id=decision_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/constraints/{constraint_id}", response_model=ConstraintOut)
def update_constraint(
    constraint_id: int, payload: ConstraintUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Constraint not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/constraints/{constraint_id}", status_code=204)
def delete_constraint(
    constraint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Constraint not found")
    db.delete(c)
    db.commit()
