from sqlalchemy.orm import Session
import logging
from .models import Interaction

logger = logging.getLogger("app.db")


def log_interaction(db: Session, question: str, answer: str) -> Interaction:
    """Store a question-answer interaction in the database."""
    logger.debug("Logging interaction to database")
    if not question or not answer:
        logger.warning("Empty question or answer provided")
    try:
        rec = Interaction(question=question, answer=answer)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        logger.info("Interaction stored with id %s", rec.id)
        return rec
    except Exception as exc:
        db.rollback()
        logger.error("Failed to log interaction: %s", exc)
        raise


def get_history(db: Session, limit: int = 10) -> list[Interaction]:
    """Retrieve the latest interactions from the database."""
    logger.debug("Fetching last %d interactions", limit)
    try:
        return (
            db.query(Interaction)
              .order_by(Interaction.ts.desc())
              .limit(limit)
              .all()
        )
    except Exception as exc:
        logger.error("Failed to fetch history: %s", exc)
        raise
