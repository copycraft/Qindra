from sqlmodel import SQLModel, create_engine, Session
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "qindra")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "qindra_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "qindra")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from . import models
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session