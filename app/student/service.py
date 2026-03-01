# app/student/service.py
from fastapi import HTTPException
from app.core.db.session import SessionLocal
from app.student.models import Student
from app.core.auth import hash_password, verify_password

def signup_student(username: str, password: str):
    db = SessionLocal()  # directly create a session
    existing = db.query(Student).filter(Student.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="username_taken")
    student = Student(username=username, hashed_password=hash_password(password))
    db.add(student)
    db.commit()
    db.refresh(student)
    db.close()
    return {"id": student.id, "username": student.username}

def login_student(username: str, password: str):
    db = SessionLocal()
    student = db.query(Student).filter(Student.username == username).first()
    if not student or not verify_password(password, student.hashed_password):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    db.close()
    return {"id": student.id, "username": student.username}