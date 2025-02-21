import logging

from app.core.security import hash_password
from app.db.models import User
from app.db.session import Base, SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)

    # Create superuser
    db = SessionLocal()
    if not db.query(User).filter(User.email == "admin@mail.com").first():
        superuser = User(
            username="admin",
            email="admin@mail.com",
            hashed_password=hash_password("123123"),
        )
        db.add(superuser)
        db.commit()
        logger.info("Superuser created: admin@mail.com")
    db.close()


if __name__ == "__main__":
    init_db()
