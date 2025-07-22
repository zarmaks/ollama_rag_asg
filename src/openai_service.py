import os
import logging
from typing import List

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
except Exception:  # pragma: no cover - missing optional deps
    ChatOpenAI = None
    OpenAIEmbeddings = None
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document

from .rag import FACTUAL_FAQ_PROMPT

logger = logging.getLogger("app.openai")


class OpenAIRAGService:
    """RAG service using OpenAI models."""

    def __init__(self, docs: List[Document]) -> None:
        logger.debug("Setting up OpenAIRAGService with %d documents", len(docs))
        if ChatOpenAI is None or OpenAIEmbeddings is None:
            raise ImportError("langchain-openai package is required")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        chat_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

        self.emb = OpenAIEmbeddings(model=embed_model, openai_api_key=api_key)
        self._log_embedding_cost(docs, embed_model)
        self.vdb = Chroma.from_documents(docs, self.emb, persist_directory="chroma_db")

        bm25 = BM25Retriever.from_documents(docs, k=3)
        sem = self.vdb.as_retriever(search_kwargs={"k": 3})
        self.retriever = EnsembleRetriever(retrievers=[sem, bm25], weights=[0.6, 0.4])

        prompt = ChatPromptTemplate.from_template(FACTUAL_FAQ_PROMPT)
        llm = ChatOpenAI(model=chat_model, temperature=0.3, openai_api_key=api_key)

        self.chain = (
            {"context": self._ctx, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def _ctx(self, inputs) -> str:
        question = inputs["query"] if isinstance(inputs, dict) else str(inputs)
        docs = self.retriever.invoke(question)
        logger.debug("Retrieved %d documents for context", len(docs))
        return "\n\n".join(d.page_content for d in docs)

    def answer(self, question: str) -> str:
        try:
            return self.chain.invoke({"query": question})
        except Exception as e:
            logger.error(f"OpenAI RAG service failed: {e}")
            return "I'm sorry, I'm having trouble processing your question right now."

    def _log_embedding_cost(self, docs: List[Document], model: str) -> None:
        try:
            import tiktoken
        except ImportError:  # pragma: no cover - runtime warning
            logger.warning("tiktoken not installed; skipping cost estimation")
            return

        enc = tiktoken.encoding_for_model(model)
        total_tokens = sum(len(enc.encode(d.page_content)) for d in docs)
        cost_per_1k = float(os.getenv("OPENAI_EMBED_COST", "0.00002"))
        est = total_tokens / 1000 * cost_per_1k
        logger.info("Estimated embedding tokens: %d (~$%.4f)", total_tokens, est)


class OpenAIContextInjectionService:
    """Context injection service using OpenAI models."""

    def __init__(self, docs: List[Document]) -> None:
        logger.debug(
            "Setting up OpenAIContextInjectionService with %d documents", len(docs)
        )
        if ChatOpenAI is None:
            raise ImportError("langchain-openai package is required")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        chat_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

        self.full_context = "\n\n".join(doc.page_content for doc in docs)

        prompt = ChatPromptTemplate.from_template(FACTUAL_FAQ_PROMPT)
        llm = ChatOpenAI(model=chat_model, temperature=0.3, openai_api_key=api_key)

        self.chain = (
            {"context": lambda _: self.full_context, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def answer(self, question: str) -> str:
        try:
            return self.chain.invoke({"query": question})
        except Exception as e:
            logger.error(f"OpenAI context injection failed: {e}")
            return "I'm sorry, I'm having trouble processing your question right now."
