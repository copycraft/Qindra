# quiz/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.db.db import Base

class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    questions = relationship("Question", back_populates="quiz")


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    text = Column(String, nullable=False)
    points = Column(Integer, default=1)  # 1x, 2x, 5x multipliers
    options = relationship("QuestionOption", back_populates="question")
    answers = relationship("Answer", back_populates="question")

    quiz = relationship("Quiz", back_populates="questions")


class QuestionOption(Base):
    __tablename__ = "question_option"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id"))
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="options")


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    question_id = Column(Integer, ForeignKey("question.id"))
    option_id = Column(Integer, ForeignKey("question_option.id"))  # which option student picked
    text = Column(String, nullable=True)  # optional free-text
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")