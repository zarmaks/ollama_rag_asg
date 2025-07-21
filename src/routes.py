from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import Generator
from .database import SessionLocal, Base, engine
from .parser import load_knowledge
from .rag import FAQRAGService, ContextInjectionService
from . import crud, schemas

logger = logging.getLogger("app.routes")

# Initialize DB tables and RAG services on startup
logger.info("Initializing database tables")
Base.metadata.create_all(bind=engine)

logger.info("Loading knowledge base")
_docs = load_knowledge("knowledge_base.txt")

logger.info("Starting RAG services")
rag_service = FAQRAGService(_docs)
context_service = ContextInjectionService(_docs)

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ask", response_model=schemas.AnswerOut)
def ask(q: schemas.QuestionIn,
        use_context_injection: bool = True,
        db: Session = Depends(get_db)) -> dict:
    """
    Process user question and return AI-generated answer.
    
    Args:
        q: Question input from user
        use_context_injection: Use context injection instead of RAG
        db: Database session
        
    Returns:
        Dictionary with 'answer' field
    """
    # Log την είσοδο
    logger.info(f"Processing question: {q.question[:50]}...")
    
    try:
        if use_context_injection:
            logger.debug("Using context injection service")
            answer = context_service.answer(q.question)
        else:
            logger.debug("Using FAQ RAG service")
            answer = rag_service.answer(q.question)
            
        crud.log_interaction(db, q.question, answer)
        
        # Log την επιτυχία
        logger.info("Question processed successfully")
        return {"answer": answer}
        
    except Exception as e:
        # Log το error
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=list[schemas.InteractionOut])
def history(limit: int = 10,
            db: Session = Depends(get_db)) -> list:
    """
    Get history of the last n questions and answers.
    
    Args:
        limit: Maximum number of interactions to return (default: 10)
        db: Database session
        
    Returns:
        List of previous question-answer interactions with timestamps
    """
    try:
        logger.debug("Retrieving %d history records", limit)
        return crud.get_history(db, limit)
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
