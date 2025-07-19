<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# FAQ-RAG Service Development Guidelines

This is a FastAPI-based RAG (Retrieval-Augmented Generation) service that integrates Mistral LLM via Ollama for answering user queries using a knowledge base.

## Project Context
- **Backend Service**: FastAPI with SQLite database
- **LLM Integration**: Ollama with Mistral model
- **RAG Implementation**: LangChain with vector similarity (Chroma) and BM25 retrieval
- **Database**: SQLAlchemy with SQLite for query logging
- **Deployment**: Docker support included

## Code Style Guidelines
- Follow PEP 8 for Python code formatting
- Use type hints for all function parameters and return values
- Include docstrings for all classes and functions
- Handle exceptions gracefully with proper HTTP status codes
- Use dependency injection for database sessions

## Architecture Patterns
- **Modular Structure**: Separate concerns into different modules (routes, models, crud, etc.)
- **Dependency Injection**: Use FastAPI's dependency system for database sessions
- **Error Handling**: Wrap service calls in try-catch blocks and return appropriate HTTP responses
- **Configuration**: Use environment variables for configurable parameters

## LangChain Integration Notes
- Use OllamaEmbeddings with "nomic-embed-text" model for embeddings
- Combine semantic search (Chroma) with keyword search (BM25) using EnsembleRetriever
- Design prompts that clearly define the assistant's role and context usage
- Handle cases where answers are not found in the knowledge base

## Database Best Practices
- Use SQLAlchemy ORM for database operations
- Implement proper session management with dependency injection
- Include timestamps for all user interactions
- Design schemas that support query history and analytics
