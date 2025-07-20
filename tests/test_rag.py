import pytest
from unittest.mock import Mock, patch
from src.rag import FAQRAGService
from langchain.schema import Document


def test_answer_returns_string():
    """Test that answer() returns a string."""
    # Prepare a dummy document
    docs = [Document(page_content="Q: x\nA: y")]
    
    # Mock the chain.invoke method to return a predictable string
    with patch.object(FAQRAGService, '__init__', lambda x, y: None):
        rag = FAQRAGService([])
        rag.chain = Mock()
        rag.chain.invoke.return_value = "mocked response"
        
        # Call answer() and verify type
        ans = rag.answer("x")
        assert isinstance(ans, str)
        assert ans == "mocked response"


def test_ctx_method():
    """Test the _ctx method returns formatted context."""
    docs = [Document(page_content="Q: test\nA: answer")]
    
    with patch.object(FAQRAGService, '__init__', lambda x, y: None):
        rag = FAQRAGService([])
        rag.retriever = Mock()
        rag.retriever.invoke.return_value = docs
        
        context = rag._ctx("test question")
        assert isinstance(context, str)
        assert "Q: test" in context
        assert "A: answer" in context


def test_faq_rag_service_initialization():
    """Test that FAQRAGService can be initialized with documents."""
    # This test requires actual Ollama setup, so we'll mock the components
    docs = [Document(page_content="Q: test\nA: answer")]
    
    with patch('src.rag.OllamaEmbeddings'), \
         patch('src.rag.Chroma'), \
         patch('src.rag.BM25Retriever'), \
         patch('src.rag.OllamaLLM'), \
         patch('src.rag.ChatPromptTemplate'), \
         patch('src.rag.EnsembleRetriever'):
        
        # This should not raise an exception
        rag = FAQRAGService(docs)
        assert rag is not None
