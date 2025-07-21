from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from typing import List
import logging

# --- PROMPT TEMPLATES ---
# Old template (for research/comparison)
OLD_FAQ_PROMPT = (
    "You are a helpful FAQ assistant.\n"
    "Based on the following Q&A pairs, answer the user's question.\n"
    "If the answer is not in the context, say so politely.\n\n"
    "Context:\n{context}\n\n"
    "Question: {query}\n\n"
    "Answer:"
)

# New factual prompt (used in both services)
FACTUAL_FAQ_PROMPT = (
    "You are a factual FAQ assistant.\n"
    "Answer **only** with sentences copied verbatim from the provided CONTEXT.\n"
    "If none of the context sentences answer the question, reply exactly:\n"
    '   "I\'m not sure based on our docs."\n\n'
    "--------\n\n"
    "### EXAMPLE 1\n"
    "CONTEXT:\n"
    '"Q: What is your refund policy?\n'
    'A: Annual plans may be cancelled within 30 days for a prorated refund."\n\n'
    "Q: What is your refund policy?\n"
    "A: Annual plans may be cancelled within 30 days for a prorated refund.\n\n"
    "--------\n\n"
    "### EXAMPLE 2\n"
    "CONTEXT:\n"
    '"Q: How do I reset my password?\n'
    "A: Click 'Forgot password?' on the login page and follow the link.\"\n\n"
    "Q: Can I deploy on Kubernetes?\n"
    "A: I'm not sure based on our docs.\n\n"
    "--------\n\n"
    "### EXAMPLE 3\n"
    "CONTEXT:\n"
    '"Q: How do I reset my password?\n'
    "A: Click 'Forgot password?' on the login page and follow the link.\"\n\n"
    "Q: Can I reset my memory card?\n"
    "A: I'm not sure based on our docs.\n\n"
    "--------\n\n"
    "### NOW\n"
    "CONTEXT:\n"
    "{context}\n\n"
    "Q: {query}\n"
    "A:"
)

logger = logging.getLogger("app.rag")


class FAQRAGService:
    def __init__(self, docs: List[Document]) -> None:
        """
        Initialize RAG service with embeddings, vector store, and retrievers.

        Args:
            docs: List of Document objects containing Q&A pairs
        """
        logger.debug("Setting up FAQRAGService with %d documents", len(docs))
        self.emb = OllamaEmbeddings(
            model="nomic-embed-text", base_url="http://localhost:11434"
        )
        self.vdb = Chroma.from_documents(docs, self.emb, persist_directory="chroma_db")
        bm25 = BM25Retriever.from_documents(docs, k=3)
        sem = self.vdb.as_retriever(search_kwargs={"k": 3})
        # self.retriever = bm25  # Use BM25Retriever as the primary retriever
        self.retriever = EnsembleRetriever(retrievers=[sem, bm25], weights=[0.6, 0.4])

        # Use the new factual prompt for RAG
        prompt = ChatPromptTemplate.from_template(FACTUAL_FAQ_PROMPT)
        llm = OllamaLLM(
            model="mistral", base_url="http://localhost:11434", temperature=0.3
        )

        self.chain = (
            {"context": self._ctx, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def _ctx(self, inputs) -> str:
        """Extract context from retrieved documents for the given question."""
        question = inputs["query"] if isinstance(inputs, dict) else str(inputs)
        docs = self.retriever.invoke(question)
        logger.debug("Retrieved %d documents for context", len(docs))
        return "\n\n".join(d.page_content for d in docs)

    def answer(self, question: str) -> str:
        """Return the LLM-generated answer for the given question."""
        try:
            return self.chain.invoke({"query": question})
        except Exception as e:
            logger.error(f"RAG service failed: {e}")
            return "I'm sorry, I'm having trouble processing your question right now."


class ContextInjectionService:
    def __init__(self, docs: List[Document]) -> None:
        """
        Initialize context injection service with full knowledge base.

        Args:
            docs: List of Document objects containing Q&A pairs
        """
        logger.debug("Setting up ContextInjectionService with %d documents", len(docs))
        # Store all document content as a single context string
        self.full_context = "\n\n".join(doc.page_content for doc in docs)

        # Use the new factual prompt for context injection
        prompt = ChatPromptTemplate.from_template(FACTUAL_FAQ_PROMPT)
        llm = OllamaLLM(
            model="mistral", base_url="http://localhost:11434", temperature=0.3
        )

        self.chain = (
            {"context": lambda x: self.full_context, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def answer(self, question: str) -> str:
        """Return the LLM-generated answer for the given question."""
        try:
            return self.chain.invoke({"query": question})
        except Exception as e:
            logger.error(f"Context injection service failed: {e}")
            return "I'm sorry, I'm having trouble processing your question right now."
