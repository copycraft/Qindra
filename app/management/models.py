# management/models.py
from sqlalchemy import Column, Integer, String
from app.core.db.db import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")  # e.g., "admin" or "teacher"