from pydantic import BaseModel

class StudentLogin(BaseModel):
    username: str
    password: str  # whatever you use to verify students

class AnswerSubmission(BaseModel):
    question_id: int
    answer: str

class QuizQuestion(BaseModel):
    id: int
    question_text: str
    options: list[str] | None = None  # if multiple choice