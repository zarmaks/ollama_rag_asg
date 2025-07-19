import re
from langchain.schema import Document

_QA_RE = re.compile(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n---|\Z)", re.S)

def load_knowledge(path: str) -> list[Document]:
    """
    Load Q/A pairs from a text file and return list of Document objects.
    """
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    pairs = _QA_RE.findall(raw)
    return [
        Document(
            page_content=f"Q: {q.strip()}\nA: {a.strip()}",
            metadata={"question": q.strip()}
        )
        for q, a in pairs
    ]
