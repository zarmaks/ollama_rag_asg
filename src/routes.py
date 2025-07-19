from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from .parser import load_knowledge
from .rag import FAQRAGService
from . import crud, schemas

# Initialize DB tables and RAG service on startup
Base.metadata.create_all(bind=engine)
_docs = load_knowledge("knowledge_base.txt")
rag_service = FAQRAGService(_docs)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ask", response_model=schemas.AnswerOut)
def ask(q: schemas.QuestionIn, db: Session = Depends(get_db)):
    try:
        answer = rag_service.answer(q.question)
        crud.log_interaction(db, q.question, answer)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=list[schemas.InteractionOut])
def history(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_history(db, limit)
