from app.core.security import hash_password
from app.db.models import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session


def create_new_user(user: UserCreate, db: Session):
    """Create a new user with a unique email."""
    if db.query(User).filter(User.email == user.email).first():
        return None

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_email(email: str, db: Session):
    """Retrieve a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session):
    """Retrieve all users."""
    return db.query(User).all()


def update_existing_user(user_update: UserCreate, db: Session):
    """Update user details."""
    db_user = db.query(User).filter(User.email == user_update.email).first()
    if not db_user:
        return None

    db_user.username = user_update.username
    db_user.hashed_password = hash_password(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_existing_user(email: str, db: Session):
    """Delete a user."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    db.delete(user)
    db.commit()
    return user
