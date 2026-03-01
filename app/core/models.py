from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = "teacher"

    quizzes: List["Quiz"] = Relationship(back_populates="owner")

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    owner_id: str = Field(foreign_key="user.id")
    questions: List["Question"] = Relationship(back_populates="quiz")
    sessions: List["GameSession"] = Relationship(back_populates="quiz")
    owner: Optional[User] = Relationship(back_populates="quizzes")

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    text: str
    question_type: str = "multiple_choice"
    options: Optional[str] = None
    correct: Optional[str] = None
    time_limit: int = 20

    quiz: Optional[Quiz] = Relationship(back_populates="questions")
    answers: List["Answer"] = Relationship(back_populates="question")

class GameSession(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    status: str = "waiting"
    started_at: Optional[float] = None
    ended_at: Optional[float] = None
    room_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:6])
    current_question_index: int = -1

    quiz: Optional[Quiz] = Relationship(back_populates="sessions")
    players: List["Player"] = Relationship(back_populates="session")

class Player(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    name: str
    session_id: str = Field(foreign_key="gamesession.id")
    score: int = 0
    xp: int = 0

    session: Optional[GameSession] = Relationship(back_populates="players")
    answers: List["Answer"] = Relationship(back_populates="player")

class Answer(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    player_id: str = Field(foreign_key="player.id")
    question_id: int = Field(foreign_key="question.id")
    selected: str
    received_at: float
    score: int

    player: Optional[Player] = Relationship(back_populates="answers")
    question: Optional[Question] = Relationship(back_populates="answers")