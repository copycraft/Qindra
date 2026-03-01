# management/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Any

# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Questions & Quizzes ----------
class QuestionCreate(BaseModel):
    text: str
    options: Optional[List[str]] = []
    correct: Optional[List[int]] = []
    time_limit: Optional[int] = 20
    question_type: Optional[str] = "multiple_choice"

class QuestionOut(BaseModel):
    id: int
    text: str
    options: Optional[List[str]] = []
    correct: Optional[List[int]] = []
    time_limit: int
    question_type: str

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = []

class QuizOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    questions: List[QuestionOut] = []

# ---------- Sessions ----------
class SessionCreate(BaseModel):
    quiz_id: int
    # optional overrides in future (max_players, settings)
    room_code: Optional[str] = None

class SessionOut(BaseModel):
    id: str
    quiz_id: int
    status: str
    room_code: Optional[str]
    started_at: Optional[float]
    ended_at: Optional[float]
    current_question_index: Optional[int] = None

class SessionResultPlayer(BaseModel):
    player_id: str
    name: str
    score: int

class SessionResults(BaseModel):
    session_id: str
    leaderboard: List[SessionResultPlayer]
    question_stats: Optional[Any] = None