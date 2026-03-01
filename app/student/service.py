from fastapi import HTTPException
from app.db.session import SessionLocal
from app.management.crud import get_user_by_username  # or your existing user fetching logic
from app.core.auth import verify_password  # or however you verify login
from app.quiz.crud import get_question_by_id, create_answer, get_quiz_for_student  # placeholder imports

def login_student(username: str, password: str):
    db = SessionLocal()
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": user.username, "id": user.id}

def get_quiz(student_id: int):
    db = SessionLocal()
    quiz = get_quiz_for_student(db, student_id)  # returns list of QuizQuestion
    return quiz

def submit_answer(student_id: int, question_id: int, answer: str):
    db = SessionLocal()
    question = get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    create_answer(db, student_id, question_id, answer)
    return {"status": "ok"}