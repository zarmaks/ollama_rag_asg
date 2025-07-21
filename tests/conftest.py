import pytest
import tempfile
import os
from pathlib import Path
from src.database import Base, engine


@pytest.fixture
def temp_knowledge_base():
    """Create a temporary knowledge base file for testing."""
    content = """Q: What is CloudSphere Platform?
A: CloudSphere Platform is a unified cloud-native application suite.

---

Q: How much does it cost?
A: Essential tier starts at $49/month.

---

Q: Do you offer a free trial?
A: Yes, we offer a 14-day free trial with $100 in platform credits.
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test."""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test
    Base.metadata.drop_all(bind=engine)
