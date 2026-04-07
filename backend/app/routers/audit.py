from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.collaboration import AuditLog
from app.schemas.collaboration import AuditLogOut
from app.core.deps import require_roles

router = APIRouter(tags=["Audit"])


@router.get("/audit", response_model=List[AuditLogOut])
def list_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
