from app.db.session import get_db
from app.schemas.token import LogoutRequest, Token
from app.schemas.user import UserLogin
from app.services.auth_service import (
    authenticate_user,
    logout_user,
    refresh_access_token,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.
    """
    tokens = authenticate_user(user.email, user.password, db)
    if not tokens:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return tokens


@router.post("/refresh", response_model=Token)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using the refresh token.
    """
    new_access_token = refresh_access_token(refresh_token, db)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    """
    Logout user by invalidating the refresh token.
    """
    logout_user(request.refresh_token, db)
    return {"message": "Logout successful"}
