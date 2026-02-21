from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=UserResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return UserResponse.model_validate(user)


@router.post("/register", response_model=UserResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(
            db, body.name, body.email, body.password
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify", response_model=UserResponse)
async def verify(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
