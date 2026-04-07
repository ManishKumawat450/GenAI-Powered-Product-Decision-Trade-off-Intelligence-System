from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.decision import Option
from app.schemas.decision import OptionCreate, OptionUpdate, OptionOut
from app.core.deps import get_current_user

router = APIRouter(tags=["Options"])


@router.get("/decisions/{decision_id}/options", response_model=List[OptionOut])
def list_options(decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Option).filter(Option.decision_id == decision_id).order_by(Option.order).all()


@router.post("/decisions/{decision_id}/options", response_model=OptionOut, status_code=201)
def create_option(
    decision_id: int, payload: OptionCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    opt = Option(**payload.model_dump(), decision_id=decision_id)
    db.add(opt)
    db.commit()
    db.refresh(opt)
    return opt


@router.put("/options/{option_id}", response_model=OptionOut)
def update_option(
    option_id: int, payload: OptionUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    opt = db.query(Option).filter(Option.id == option_id).first()
    if not opt:
        raise HTTPException(status_code=404, detail="Option not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(opt, k, v)
    db.commit()
    db.refresh(opt)
    return opt


@router.delete("/options/{option_id}", status_code=204)
def delete_option(
    option_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    opt = db.query(Option).filter(Option.id == option_id).first()
    if not opt:
        raise HTTPException(status_code=404, detail="Option not found")
    db.delete(opt)
    db.commit()
