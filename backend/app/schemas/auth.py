import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    workspace_id: str
    iat: int | None = None
    exp: int | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    role: str
    workspace_id: uuid.UUID
