from app.api import auth, rag, user
from app.db.init_db import init_db
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()


# Rag system
app.include_router(rag.router, prefix="/rag", tags=["Rag"])

# User management
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/user", tags=["User"])
