import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src import crud
from src.models import Interaction


@pytest.fixture
def db_session():
    """Provide a Session connected to an in-memory SQLite DB."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_log_interaction(db_session):
    """log_interaction should store a record in the DB."""
    rec = crud.log_interaction(db_session, "Q1", "A1")
    assert isinstance(rec, Interaction)
    assert rec.id is not None
    stored = db_session.query(Interaction).first()
    assert stored.question == "Q1"
    assert stored.answer == "A1"


def test_get_history(db_session):
    """get_history should return interactions ordered by ts desc."""
    crud.log_interaction(db_session, "Q1", "A1")
    crud.log_interaction(db_session, "Q2", "A2")
    hist = crud.get_history(db_session, limit=2)
    assert len(hist) == 2
    # Check that we got both interactions
    questions = [h.question for h in hist]
    assert "Q1" in questions
    assert "Q2" in questions
