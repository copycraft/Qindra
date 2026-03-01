from pydantic import BaseModel
from typing import List, Optional

class StudentCreate(BaseModel):
    username: str
    password: str

class StudentLogin(BaseModel):
    username: str
    password: str

class AnswerSubmission(BaseModel):
    question_id: int
    answer: str

class QuizQuestion(BaseModel):
    id: int
    question_text: str
    options: Optional[List[str]] = None