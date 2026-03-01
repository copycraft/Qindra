from pydantic import BaseModel
from typing import Optional, List

class QuestionCreate(BaseModel):
    text: str
    options: Optional[List[str]] = []
    correct: Optional[List[int]] = []
    time_limit: Optional[int] = 20
    question_type: Optional[str] = "multiple_choice"

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = []

class QuestionOut(BaseModel):
    id: int
    text: str
    options: Optional[List[str]] = []
    time_limit: int
    question_type: str

class QuizOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    questions: List[QuestionOut] = []