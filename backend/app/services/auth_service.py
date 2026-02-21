import uuid

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import TokenPayload


def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.NEXTAUTH_SECRET, algorithms=["HS256"]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def register_user(
    db: AsyncSession, name: str, email: str, password: str
) -> User:
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise ValueError("User with this email already exists")

    # Create workspace
    workspace = Workspace(id=uuid.uuid4(), name=f"{name}'s Workspace")
    db.add(workspace)
    await db.flush()

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        name=name,
        role="admin",
        workspace_id=workspace.id,
    )
    db.add(user)
    await db.flush()

    return user
