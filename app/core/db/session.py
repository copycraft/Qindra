# app/core/db/session.py
from sqlalchemy.orm import sessionmaker
from app.core.db.db import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)