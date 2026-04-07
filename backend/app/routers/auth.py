from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User, Role
from app.models.collaboration import AuditLog
from app.schemas.auth import UserCreate, UserLogin, Token, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


def _log_audit(db: Session, user_id: int, action: str, details: dict | None = None):
    log = AuditLog(user_id=user_id, action=action, resource_type="auth", details=details,
                   timestamp=datetime.utcnow())
    db.add(log)
    db.commit()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    role = db.query(Role).filter(Role.name == payload.role).first()
    if not role:
        role = Role(name=payload.role)
        db.add(role)
        db.flush()

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    _log_audit(db, user.id, "register", {"email": user.email})
    return UserOut(
        id=user.id, email=user.email, username=user.username,
        is_active=user.is_active, roles=[r.name for r in user.roles]
    )


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")

    token = create_access_token({"sub": str(user.id)})
    _log_audit(db, user.id, "login")
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id, email=current_user.email, username=current_user.username,
        is_active=current_user.is_active, roles=[r.name for r in current_user.roles]
    )
