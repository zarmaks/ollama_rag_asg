import re
import logging
from langchain.schema import Document

logger = logging.getLogger("app.parser")

_QA_RE = re.compile(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n---|\Z)", re.S)


def load_knowledge(path: str) -> list[Document]:
    """Load Q/A pairs from a text file."""
    logger.debug("Loading knowledge base from %s", path)
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except Exception as exc:
        logger.error("Failed to read knowledge base: %s", exc)
        raise

    pairs = _QA_RE.findall(raw)
    logger.info("Loaded %d Q&A pairs", len(pairs))
    return [
        Document(
            page_content=f"Q: {q.strip()}\nA: {a.strip()}",
            metadata={"question": q.strip()},
        )
        for q, a in pairs
    ]
