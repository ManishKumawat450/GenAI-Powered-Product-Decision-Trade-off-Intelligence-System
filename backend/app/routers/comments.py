from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.collaboration import Comment
from app.schemas.collaboration import CommentCreate, CommentUpdate, CommentOut
from app.core.deps import get_current_user

router = APIRouter(tags=["Comments"])


@router.get("/decisions/{decision_id}/comments", response_model=List[CommentOut])
def list_comments(decision_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Comment).filter(Comment.decision_id == decision_id)\
        .order_by(Comment.created_at).all()


@router.post("/decisions/{decision_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(
    decision_id: int, payload: CommentCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = Comment(**payload.model_dump(), decision_id=decision_id, author_id=current_user.id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int, payload: CommentUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    c.content = payload.content
    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)
    return c


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    c = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(c)
    db.commit()
