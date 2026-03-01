from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("QINDRA_DB", "sqlite:///./qindra.db")  # default SQLite, swap to postgres://user:pass@host/db

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from ..core.models import User, Quiz, Question, GameSession, Player, Answer
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session