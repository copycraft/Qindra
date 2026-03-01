import subprocess
import time
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Base model
Base = declarative_base()

# ====================
# Your Models
# ====================

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="player")

class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)

class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    text = Column(Text, nullable=False)
    quiz = relationship("Quiz", back_populates="questions")

Quiz.questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

class GameSession(Base):
    __tablename__ = "gamesession"
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    active = Column(Boolean, default=True)

class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    session_id = Column(Integer, ForeignKey("gamesession.id"))

class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("question.id"))
    player_id = Column(Integer, ForeignKey("player.id"))
    text = Column(Text, nullable=False)
    correct = Column(Boolean, default=False)

# ====================
# Start Docker PostgreSQL
# ====================

DB_NAME = "qindra"
DB_USER = "qindra"
DB_PASS = "qindra123"
DB_PORT = "5432"
CONTAINER_NAME = "qindra_db"

# Start PostgreSQL container
subprocess.run([
    "docker", "run", "-d",
    "--name", CONTAINER_NAME,
    "-e", f"POSTGRES_USER={DB_USER}",
    "-e", f"POSTGRES_PASSWORD={DB_PASS}",
    "-e", f"POSTGRES_DB={DB_NAME}",
    "-p", f"{DB_PORT}:5432",
    "postgres:15-alpine"
], check=False)

print("Waiting for PostgreSQL to start...")
time.sleep(10)  # wait for container to be ready

# ====================
# Connect to DB
# ====================

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@localhost:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

# Create tables
Base.metadata.create_all(engine)

print("Database initialized successfully!")