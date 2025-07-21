from sqlalchemy import Column, Integer, Text, DateTime, func
from .database import Base


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    ts = Column(DateTime, server_default=func.now())
