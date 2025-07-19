from sqlalchemy.orm import Session
from .models import Interaction


def log_interaction(db: Session, question: str, answer: str) -> Interaction:
    rec = Interaction(question=question, answer=answer)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_history(db: Session, limit: int = 10) -> list[Interaction]:
    return (
        db.query(Interaction)
          .order_by(Interaction.ts.desc())
          .limit(limit)
          .all()
    )
