from sqlmodel import Session, select
from .models import Quiz, Question
from .schemas import QuizCreate, QuestionCreate
import json

# ---------- Quiz ----------

def create_quiz(session: Session, payload: QuizCreate, owner_id: str) -> Quiz:
    quiz = Quiz(title=payload.title, description=payload.description, owner_id=owner_id)
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    for q in payload.questions or []:
        create_question(session, quiz.id, q)
    session.refresh(quiz)
    return quiz

def get_quiz(session: Session, quiz_id: int, owner_id: str) -> Quiz | None:
    statement = select(Quiz).where(Quiz.id == quiz_id, Quiz.owner_id == owner_id)
    return session.exec(statement).first()

def list_quizzes(session: Session, owner_id: str):
    statement = select(Quiz).where(Quiz.owner_id == owner_id)
    return session.exec(statement).all()

def update_quiz(session: Session, quiz_id: int, owner_id: str, title: str = None, description: str = None):
    quiz = get_quiz(session, quiz_id, owner_id)
    if not quiz:
        return None
    if title:
        quiz.title = title
    if description:
        quiz.description = description
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    return quiz

def delete_quiz(session: Session, quiz_id: int, owner_id: str):
    quiz = get_quiz(session, quiz_id, owner_id)
    if not quiz:
        return False
    session.delete(quiz)
    session.commit()
    return True

# ---------- Question ----------

def create_question(session: Session, quiz_id: int, payload: QuestionCreate) -> Question:
    qrow = Question(
        quiz_id=quiz_id,
        text=payload.text,
        time_limit=payload.time_limit or 20,
        question_type=payload.question_type or "multiple_choice",
        options=json.dumps(payload.options or []),
        correct=json.dumps(payload.correct) if payload.correct is not None else None
    )
    session.add(qrow)
    session.commit()
    session.refresh(qrow)
    return qrow

def update_question(session: Session, question_id: int, quiz_id: int, payload: QuestionCreate):
    statement = select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    question = session.exec(statement).first()
    if not question:
        return None
    question.text = payload.text or question.text
    question.question_type = payload.question_type or question.question_type
    question.time_limit = payload.time_limit or question.time_limit
    question.options = json.dumps(payload.options or json.loads(question.options or "[]"))
    question.correct = json.dumps(payload.correct or json.loads(question.correct or "[]"))
    session.add(question)
    session.commit()
    session.refresh(question)
    return question

def delete_question(session: Session, question_id: int, quiz_id: int):
    statement = select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    question = session.exec(statement).first()
    if not question:
        return False
    session.delete(question)
    session.commit()
    return True