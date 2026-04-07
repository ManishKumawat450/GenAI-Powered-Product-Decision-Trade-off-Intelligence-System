from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.collaboration import AuditLog
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceOut
from app.core.deps import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


def _audit(db: Session, user_id: int, action: str, resource_id: int, details: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource_type="workspace",
                    resource_id=resource_id, details=details, timestamp=datetime.utcnow()))
    db.commit()


@router.get("", response_model=List[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()


@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ws = Workspace(**payload.model_dump(), owner_id=current_user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    _audit(db, current_user.id, "create_workspace", ws.id, {"name": ws.name})
    return ws


@router.get("/{workspace_id}", response_model=WorkspaceOut)
def get_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.put("/{workspace_id}", response_model=WorkspaceOut)
def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(ws, k, v)
    ws.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ws)
    _audit(db, current_user.id, "update_workspace", ws.id)
    return ws


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.owner_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(ws)
    db.commit()
    _audit(db, current_user.id, "delete_workspace", workspace_id)
