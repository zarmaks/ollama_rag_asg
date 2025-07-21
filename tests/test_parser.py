from src.parser import load_knowledge


def test_load_knowledge(tmp_path):
    """Test loading knowledge from a temporary file."""
    # Create a temporary knowledge base file
    content = "Q: test?\nA: answer.\n---"
    file = tmp_path / "kb.txt"
    file.write_text(content)

    # Load documents
    docs = load_knowledge(str(file))
    assert len(docs) == 1
    assert "test?" in docs[0].page_content
    assert "answer." in docs[0].page_content
    assert docs[0].metadata["question"] == "test?"


def test_load_knowledge_multiple_qa(tmp_path):
    """Test loading multiple Q&A pairs."""
    content = """Q: First question?
A: First answer.

---

Q: Second question?
A: Second answer.

---"""
    file = tmp_path / "kb.txt"
    file.write_text(content)

    docs = load_knowledge(str(file))
    assert len(docs) == 2
    assert "First question?" in docs[0].page_content
    assert "Second question?" in docs[1].page_content


def test_load_knowledge_empty_file(tmp_path):
    """Test loading from an empty file."""
    file = tmp_path / "empty.txt"
    file.write_text("")

    docs = load_knowledge(str(file))
    assert len(docs) == 0
