from pydantic import BaseModel
from datetime import datetime


class QuestionIn(BaseModel):
    question: str


class AnswerOut(BaseModel):
    answer: str


class InteractionOut(BaseModel):
    question: str
    answer: str
    ts: datetime
