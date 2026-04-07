from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.decision import Decision, DecisionVersion
from app.models.workspace import Workspace
from app.models.collaboration import AuditLog
from app.schemas.decision import DecisionCreate, DecisionUpdate, DecisionOut, DecisionVersionOut
from app.core.deps import get_current_user

router = APIRouter(tags=["Decisions"])


def _audit(db, uid, action, rid, details=None):
    db.add(AuditLog(user_id=uid, action=action, resource_type="decision",
                    resource_id=rid, details=details, timestamp=datetime.utcnow()))
    db.commit()


def _snapshot(decision: Decision) -> dict:
    return {
        "id": decision.id, "title": decision.title,
        "problem_statement": decision.problem_statement,
        "success_metrics": decision.success_metrics, "status": decision.status,
        "updated_at": decision.updated_at.isoformat() if decision.updated_at else None,
    }


@router.get("/workspaces/{workspace_id}/decisions", response_model=List[DecisionOut])
def list_decisions(
    workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db.query(Decision).filter(Decision.workspace_id == workspace_id).all()


@router.post("/workspaces/{workspace_id}/decisions", response_model=DecisionOut, status_code=201)
def create_decision(
    workspace_id: int, payload: DecisionCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    d = Decision(**payload.model_dump(), workspace_id=workspace_id, created_by=current_user.id)
    db.add(d)
    db.commit()
    db.refresh(d)
    _audit(db, current_user.id, "create_decision", d.id, {"title": d.title})
    return d


@router.get("/decisions/{decision_id}", response_model=DecisionOut)
def get_decision(
    decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    return d


@router.put("/decisions/{decision_id}", response_model=DecisionOut)
def update_decision(
    decision_id: int, payload: DecisionUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")

    # Save version before update
    versions_count = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id).count()
    dv = DecisionVersion(
        decision_id=d.id, version_number=versions_count + 1,
        snapshot=_snapshot(d), created_by=current_user.id
    )
    db.add(dv)

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(d, k, v)
    d.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(d)
    _audit(db, current_user.id, "update_decision", d.id)
    return d


@router.delete("/decisions/{decision_id}", status_code=204)
def delete_decision(
    decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    db.delete(d)
    db.commit()
    _audit(db, current_user.id, "delete_decision", decision_id)


@router.get("/decisions/{decision_id}/versions", response_model=List[DecisionVersionOut])
def list_versions(
    decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id)\
        .order_by(DecisionVersion.version_number.desc()).all()
