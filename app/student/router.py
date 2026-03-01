from fastapi import APIRouter
from app.student import schemas, service
from app.student import models

router = APIRouter(prefix="/api/student", tags=["student"])

@router.post("/signup")
def signup(payload: schemas.StudentCreate):
    return service.signup_student(payload.username, payload.password)

@router.post("/login")
def login(payload: schemas.StudentLogin):
    return service.login_student(payload.username, payload.password)

@router.get("/quiz")
def get_quiz(student_id: int):
    return service.get_quiz(student_id)

@router.post("/quiz/answer")
def submit_answer(payload: schemas.AnswerSubmission, student_id: int):
    return service.submit_answer(student_id, payload.question_id, payload.answer)

from fastapi import Query

@router.get("/quiz")
def get_quiz(student_id: int = Query(...)):
    return service.get_quiz(student_id)

@router.post("/answer")
def submit_answer(
    student_id: int,
    payload: schemas.AnswerSubmission
):
    return service.submit_answer(
        student_id,
        payload.question_id,
        payload.answer
    )