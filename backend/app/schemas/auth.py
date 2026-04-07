from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str = "viewer"

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("admin", "pm", "viewer"):
            raise ValueError("role must be admin, pm, or viewer")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    roles: List[str] = []

    model_config = {"from_attributes": True}
