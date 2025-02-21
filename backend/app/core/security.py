from datetime import datetime, timedelta

from app.core.config import settings
from app.db.models import RefreshToken
from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    data: dict, expires_delta: timedelta, token_type: str = "access"
) -> str:
    """Generate an access token with an expiration time."""
    expire = datetime.utcnow() + expires_delta
    data.update({"exp": expire, "type": token_type})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode token"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_refresh_token(user_id: dict, db: Session) -> str:
    """Generate and store a refresh token in the database."""
    refresh_token = create_token(
        {"sub": user_id}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )

    db_token = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=datetime.utcnow()
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()

    return refresh_token
