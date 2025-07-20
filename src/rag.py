from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.retrievers import EnsembleRetriever


class FAQRAGService:
    def __init__(self, docs):
        """
        Initialize embeddings, vector store, retrievers, prompt, and chain.
        """
        self.emb = OllamaEmbeddings(model="nomic-embed-text",
                                    base_url="http://localhost:11434")
        self.vdb = Chroma.from_documents(docs, self.emb,
                                         persist_directory="chroma_db")
        bm25 = BM25Retriever.from_documents(docs, k=3)
        sem = self.vdb.as_retriever(search_kwargs={"k": 3})
        #self.retriever = bm25  # Use BM25Retriever as the primary retriever
        self.retriever = EnsembleRetriever(
            retrievers=[sem, bm25],
            weights=[0.6, 0.4]
        )


        template = (
            "You are a helpful FAQ assistant.\n"
            "Based on the following Q&A pairs, answer the user's question.\n"
            "If the answer is not in the context, say so politely.\n\n"
            "Context:\n{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        )
        prompt = ChatPromptTemplate.from_template(template)
        llm = OllamaLLM(model="mistral",
                     base_url="http://localhost:11434",
                     temperature=0.3)

        self.chain = (
            {"context": self._ctx, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def _ctx(self, inputs) -> str:
        # LangChain περνάει ολόκληρο το input dict στη συνάρτηση
        question = inputs["query"] if isinstance(inputs, dict) else str(inputs)
        docs = self.retriever.invoke(question)
        return "\n\n".join(d.page_content for d in docs)

    def answer(self, question: str) -> str:
        """Return the LLM-generated answer for the given question."""
        return self.chain.invoke({"query": question})


class ContextInjectionService:
    def __init__(self, docs):
        """
        Initialize with full knowledge base context injection.
        """
        # Store all document content as a single context string
        self.full_context = "\n\n".join(doc.page_content for doc in docs)
        
        template = (
            "You are a helpful FAQ assistant.\n"
            "Based on the following Q&A pairs, answer the user's question.\n"
            "If the answer is not in the context, say so politely.\n\n"
            "Context:\n{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        )
        prompt = ChatPromptTemplate.from_template(template)
        llm = OllamaLLM(model="mistral",
                        base_url="http://localhost:11434",
                        temperature=0.3)

        self.chain = (
            {"context": lambda x: self.full_context,
             "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def answer(self, question: str) -> str:
        """Return the LLM-generated answer for the given question."""
        return self.chain.invoke({"query": question})
