# management/crud.py
from sqlmodel import Session, select
from typing import Optional, List
import json
import time

from app.core.models import User, Quiz, Question, GameSession, Player, Answer
from app.management import schemas
from app.core.auth import hash_password

# ---------- User ----------
def create_user(session: Session, username: str, password: str) -> User:
    user = User(username=username, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()

def get_user_by_id(session: Session, user_id: str) -> Optional[User]:
    return session.get(User, user_id)

# ---------- Quiz ----------
def create_quiz(session: Session, payload: schemas.QuizCreate, owner_id: str) -> Quiz:
    quiz = Quiz(title=payload.title, description=payload.description, owner_id=owner_id)
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    # create questions
    for q in payload.questions or []:
        create_question(session, quiz.id, q)
    session.refresh(quiz)
    return quiz

def list_quizzes(session: Session, owner_id: str) -> List[Quiz]:
    stmt = select(Quiz).where(Quiz.owner_id == owner_id).order_by(Quiz.id)
    return session.exec(stmt).all()

def get_quiz(session: Session, quiz_id: int, owner_id: str) -> Optional[Quiz]:
    stmt = select(Quiz).where(Quiz.id == quiz_id, Quiz.owner_id == owner_id)
    return session.exec(stmt).first()

def update_quiz(session: Session, quiz_id: int, owner_id: str, title: Optional[str], description: Optional[str]) -> Optional[Quiz]:
    quiz = get_quiz(session, quiz_id, owner_id)
    if not quiz:
        return None
    if title is not None:
        quiz.title = title
    if description is not None:
        quiz.description = description
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    return quiz

def delete_quiz(session: Session, quiz_id: int, owner_id: str) -> bool:
    quiz = get_quiz(session, quiz_id, owner_id)
    if not quiz:
        return False
    session.delete(quiz)
    session.commit()
    return True

# ---------- Question ----------
def create_question(session: Session, quiz_id: int, payload: schemas.QuestionCreate) -> Question:
    qrow = Question(
        quiz_id=quiz_id,
        text=payload.text,
        question_type=payload.question_type or "multiple_choice",
        options=json.dumps(payload.options or []),
        correct=json.dumps(payload.correct or []),
        time_limit=payload.time_limit or 20
    )
    session.add(qrow)
    session.commit()
    session.refresh(qrow)
    return qrow

def update_question(session: Session, question_id: int, quiz_id: int, payload: schemas.QuestionCreate) -> Optional[Question]:
    stmt = select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    q = session.exec(stmt).first()
    if not q:
        return None
    q.text = payload.text or q.text
    q.question_type = payload.question_type or q.question_type
    q.options = json.dumps(payload.options or json.loads(q.options or "[]"))
    q.correct = json.dumps(payload.correct or json.loads(q.correct or "[]"))
    q.time_limit = payload.time_limit or q.time_limit
    session.add(q)
    session.commit()
    session.refresh(q)
    return q

def delete_question(session: Session, question_id: int, quiz_id: int) -> bool:
    stmt = select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    q = session.exec(stmt).first()
    if not q:
        return False
    session.delete(q)
    session.commit()
    return True

# ---------- Sessions ----------
def create_session(session: Session, quiz_id: int, owner_id: str, room_code: Optional[str] = None) -> Optional[GameSession]:
    # verify ownership of quiz
    quiz = session.get(Quiz, quiz_id)
    if not quiz or quiz.owner_id != owner_id:
        return None
    gs = GameSession(quiz_id=quiz_id, status="waiting", started_at=None, ended_at=None)
    if room_code:
        gs.room_code = room_code
    session.add(gs)
    session.commit()
    session.refresh(gs)
    return gs

def list_sessions(session: Session, owner_id: str) -> List[GameSession]:
    # only sessions for quizzes owned by owner_id
    stmt = select(GameSession).join(Quiz).where(Quiz.owner_id == owner_id).order_by(GameSession.id)
    return session.exec(stmt).all()

def get_session(session: Session, session_id: str, owner_id: str) -> Optional[GameSession]:
    stmt = select(GameSession).where(GameSession.id == session_id).join(Quiz).where(Quiz.owner_id == owner_id)
    return session.exec(stmt).first()

def start_session(session: Session, session_id: str, owner_id: str) -> Optional[GameSession]:
    gs = get_session(session, session_id, owner_id)
    if not gs:
        return None
    gs.status = "active"
    gs.started_at = time.time()
    # init current_question_index if not present
    if not hasattr(gs, "current_question_index") or gs.current_question_index is None:
        setattr(gs, "current_question_index", -1)
    session.add(gs)
    session.commit()
    session.refresh(gs)
    return gs

def end_session(session: Session, session_id: str, owner_id: str) -> Optional[GameSession]:
    gs = get_session(session, session_id, owner_id)
    if not gs:
        return None
    gs.status = "finished"
    gs.ended_at = time.time()
    session.add(gs)
    session.commit()
    session.refresh(gs)
    return gs

def session_results(session: Session, session_id: str, owner_id: str) -> Optional[dict]:
    gs = get_session(session, session_id, owner_id)
    if not gs:
        return None
    # build leaderboard from Player table
    stmt = select(Player).where(Player.session_id == gs.id)
    players = session.exec(stmt).all()
    leaderboard = []
    for p in players:
        leaderboard.append({"player_id": p.id, "name": p.name, "score": p.score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    # optional: question-level stats
    # pull answers grouped by question
    stmt2 = select(Answer).where(Answer.player_id.in_([p.id for p in players]))
    answers = session.exec(stmt2).all()
    qstats = {}
    for a in answers:
        qid = a.question_id
        qstats.setdefault(qid, {"answers": 0, "total_score": 0})
        qstats[qid]["answers"] += 1
        qstats[qid]["total_score"] += a.score or 0
    # convert qstats to simple structure
    qstats_out = {str(k): v for k, v in qstats.items()}
    return {"session_id": gs.id, "leaderboard": leaderboard, "question_stats": qstats_out}