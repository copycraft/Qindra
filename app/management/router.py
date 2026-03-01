# management/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import List

from app.core.db import get_session
from app.core.auth import create_access_token, decode_access_token, verify_password
from app.management import schemas, crud
from app.core.models import User
from app.core.auth import pwd_context  # not directly needed but kept

router = APIRouter(prefix="/api/management", tags=["management"])

# ---------- Auth ----------
@router.post("/signup", response_model=schemas.TokenOut, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_username(session, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="username_taken")
    user = crud.create_user(session, payload.username, payload.password)
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = crud.get_user_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# ---------- Dependency for teacher ----------
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/management/login")

def get_current_teacher(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid_token")
    user_id = payload.get("sub")
    role = payload.get("role")
    if role != "teacher":
        raise HTTPException(status_code=403, detail="forbidden")
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    return user

# ---------- Quizzes ----------
@router.post("/quizzes", response_model=schemas.QuizOut)
def create_quiz(payload: schemas.QuizCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.create_quiz(session, payload, owner_id=current_user.id)
    return quiz_to_out(quiz)

@router.get("/quizzes", response_model=List[schemas.QuizOut])
def list_quizzes(session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quizzes = crud.list_quizzes(session, current_user.id)
    return [quiz_to_out(q) for q in quizzes]

@router.get("/quizzes/{quiz_id}", response_model=schemas.QuizOut)
def get_quiz(quiz_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.get_quiz(session, quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    return quiz_to_out(quiz)

@router.put("/quizzes/{quiz_id}", response_model=schemas.QuizOut)
def update_quiz(quiz_id: int, payload: schemas.QuizCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.update_quiz(session, quiz_id, current_user.id, title=payload.title, description=payload.description)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    return quiz_to_out(quiz)

@router.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    ok = crud.delete_quiz(session, quiz_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    return {"ok": True}

# ---------- Questions ----------
@router.post("/quizzes/{quiz_id}/questions", response_model=schemas.QuestionOut)
def create_question(quiz_id: int, payload: schemas.QuestionCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.get_quiz(session, quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    q = crud.create_question(session, quiz_id, payload)
    return question_to_out(q)

@router.put("/quizzes/{quiz_id}/questions/{question_id}", response_model=schemas.QuestionOut)
def update_question(quiz_id: int, question_id: int, payload: schemas.QuestionCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.get_quiz(session, quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    q = crud.update_question(session, question_id, quiz_id, payload)
    if not q:
        raise HTTPException(status_code=404, detail="question_not_found")
    return question_to_out(q)

@router.delete("/quizzes/{quiz_id}/questions/{question_id}")
def delete_question(quiz_id: int, question_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    quiz = crud.get_quiz(session, quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz_not_found")
    ok = crud.delete_question(session, question_id, quiz_id)
    if not ok:
        raise HTTPException(status_code=404, detail="question_not_found")
    return {"ok": True}

# ---------- Sessions ----------
@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(payload: schemas.SessionCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    gs = crud.create_session(session, payload.quiz_id, current_user.id, room_code=payload.room_code)
    if not gs:
        raise HTTPException(status_code=400, detail="could_not_create_session_or_not_owner")
    return session_to_out(gs)

@router.get("/sessions", response_model=List[schemas.SessionOut])
def list_sessions(session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    sessions = crud.list_sessions(session, current_user.id)
    return [session_to_out(s) for s in sessions]

@router.get("/sessions/{session_id}", response_model=schemas.SessionOut)
def get_session(session_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    gs = crud.get_session(session, session_id, current_user.id)
    if not gs:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session_to_out(gs)

@router.post("/sessions/{session_id}/start", response_model=schemas.SessionOut)
def start_session(session_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    gs = crud.start_session(session, session_id, current_user.id)
    if not gs:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session_to_out(gs)

@router.post("/sessions/{session_id}/end", response_model=schemas.SessionOut)
def end_session(session_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    gs = crud.end_session(session, session_id, current_user.id)
    if not gs:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session_to_out(gs)

@router.get("/sessions/{session_id}/results", response_model=schemas.SessionResults)
def session_results(session_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_teacher)):
    res = crud.session_results(session, session_id, current_user.id)
    if not res:
        raise HTTPException(status_code=404, detail="session_not_found")
    # map to Pydantic
    leaderboard = [schemas.SessionResultPlayer(**p) for p in res["leaderboard"]]
    return schemas.SessionResults(session_id=res["session_id"], leaderboard=leaderboard, question_stats=res.get("question_stats"))

# ---------- helpers ----------
import json
def quiz_to_out(quiz: Quiz) -> schemas.QuizOut:
    qs = []
    for q in quiz.questions:
        try:
            opts = json.loads(q.options) if q.options else []
            correct = json.loads(q.correct) if q.correct else []
        except Exception:
            opts = []
            correct = []
        qs.append(schemas.QuestionOut(
            id=q.id, text=q.text, options=opts, correct=correct, time_limit=q.time_limit, question_type=q.question_type
        ))
    return schemas.QuizOut(id=quiz.id, title=quiz.title, description=quiz.description, questions=qs)

def question_to_out(q: Question) -> schemas.QuestionOut:
    import json
    try:
        opts = json.loads(q.options) if q.options else []
        correct = json.loads(q.correct) if q.correct else []
    except Exception:
        opts = []
        correct = []
    return schemas.QuestionOut(
        id=q.id, text=q.text, options=opts, correct=correct, time_limit=q.time_limit, question_type=q.question_type
    )

def session_to_out(gs: GameSession) -> schemas.SessionOut:
    return schemas.SessionOut(
        id=gs.id,
        quiz_id=gs.quiz_id,
        status=gs.status,
        room_code=getattr(gs, "room_code", None),
        started_at=gs.started_at,
        ended_at=gs.ended_at,
        current_question_index=getattr(gs, "current_question_index", None)
    )