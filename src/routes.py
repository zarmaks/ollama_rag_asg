from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from .database import SessionLocal, Base, engine
from .parser import load_knowledge
from .rag import FAQRAGService, ContextInjectionService
from . import crud, schemas

logger = logging.getLogger(__name__)

# Initialize DB tables and RAG services on startup
Base.metadata.create_all(bind=engine)
_docs = load_knowledge("knowledge_base.txt")
rag_service = FAQRAGService(_docs)
context_service = ContextInjectionService(_docs)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ask", response_model=schemas.AnswerOut)
def ask(q: schemas.QuestionIn,
        use_context_injection: bool = False,
        db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing question: {q.question}")
        
        if use_context_injection:
            answer = context_service.answer(q.question)
        else:
            answer = rag_service.answer(q.question)
            
        crud.log_interaction(db, q.question, answer)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=list[schemas.InteractionOut])
def history(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_history(db, limit)
