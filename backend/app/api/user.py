from app.db.session import get_db
from app.schemas.user import UserCreate, UserDetail
from app.services.user_service import (
    create_new_user,
    delete_existing_user,
    get_all_users,
    get_user_by_email,
    update_existing_user,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/create_user", response_model=UserDetail)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with unique email and username."""
    new_user = create_new_user(user, db)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already taken")
    return new_user


@router.get("/get_user", response_model=UserDetail)
def get_user(email: str, db: Session = Depends(get_db)):
    """Retrieve a user by email."""
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/get_users", response_model=list[UserDetail])
def get_users(db: Session = Depends(get_db)) -> list[UserDetail]:
    """Retrieve all users."""
    return get_all_users(db)


@router.put("/update_user", response_model=UserDetail)
def update_user(user_update: UserCreate, db: Session = Depends(get_db)):
    """Update user details."""
    updated_user = update_existing_user(user_update, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/delete_user", response_model=UserDetail)
def delete_user(email: str, db: Session = Depends(get_db)):
    """Delete a user."""
    deleted_user = delete_existing_user(email, db)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
