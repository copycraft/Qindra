# app/quiz/crud.py
from sqlalchemy.orm import Session
from app.quiz.models import Quiz, Question, Answer

def get_quiz_for_student(db: Session, student_id: int):
    # For now, just return all quizzes
    return db.query(Quiz).all()

def get_question_by_id(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()

def create_answer(db: Session, student_id: int, question_id: int, text: str):
    question = get_question_by_id(db, question_id)
    if not question:
        return None

    correct = False
    if ";" in question.correct_answer:
        correct_answers = [a.strip() for a in question.correct_answer.split(";")]
        submitted_answers = [a.strip() for a in text.split(";")]
        correct = set(submitted_answers) == set(correct_answers)
    else:
        correct = text.strip() == question.correct_answer.strip()

    answer = Answer(
        student_id=student_id,
        question_id=question_id,
        text=text,
        is_correct=correct
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer

def get_answers_for_quiz(db: Session, student_id: int, quiz_id: int):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return []
    answers = []
    for question in quiz.questions:
        ans = db.query(Answer).filter(
            Answer.student_id == student_id,
            Answer.question_id == question.id
        ).all()
        answers.extend(ans)
    return answers