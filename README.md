# FAQ-RAG Service

A FastAPI-based service that integrates Mistral LLM via Ollama to answer user queries using a predefined knowledge base, with query logging and history retrieval functionality.

## Features

- **REST API** with FastAPI
- **Mistral LLM integration** via Ollama for local inference
- **RAG (Retrieval-Augmented Generation)** with vector similarity and BM25 retrieval
- **SQLite database** for query/response persistence
- **Docker support** for easy deployment

## Setup

### Prerequisites

1. Install [Ollama](https://ollama.com/)
2. Pull the required models:
   ```bash
   ollama pull mistral
   ollama pull nomic-embed-text
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd faq-rag-service
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a knowledge base file `knowledge_base.txt` with Q&A pairs (see example below)

## Usage

### Run locally

```bash
uvicorn src.main:app --reload
```

Open Swagger UI: http://localhost:8000/docs

### API Endpoints

- **POST /ask** - Submit a question and get an AI-generated answer
  ```json
  {
    "question": "What is your refund policy?"
  }
  ```

- **GET /history?n=10** - Retrieve the last N questions and answers with timestamps

### Docker

```bash
docker build -t faq-rag .
docker run -p 8000:8000 faq-rag
```

## Knowledge Base Format

Create a `knowledge_base.txt` file with the following format:

```
Q: What is the refund policy?
A: Our refund policy allows customers to return products within 30 days of purchase for a full refund.

Q: How can I contact support?
A: You can reach us via email at support@example.com or call our hotline at 1-800-SUPPORT.

Q: What are your business hours?
A: We are open Monday through Friday from 9 AM to 6 PM EST.
```

## Logging

The application uses Python's ``logging`` module. Logs are printed to
``stdout`` and grouped by category:

- ``app.routes`` – API layer
- ``app.rag`` – RAG services
- ``app.parser`` – knowledge base loader
- ``app.db`` – database operations

The default log level is ``INFO`` but ``DEBUG`` messages are available for
additional detail.

## AI Coding Assistant Usage

This project was developed with assistance from GitHub Copilot, which helped with:
- Generating boilerplate code for FastAPI routes and database models
- Creating the RAG implementation using LangChain
- Debugging import issues and dependency configurations
- Writing documentation and setup instructions

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── routes.py        # API endpoints
│   ├── rag.py          # RAG service implementation
│   ├── parser.py       # Knowledge base parser
│   ├── database.py     # Database configuration
│   ├── models.py       # SQLAlchemy models
│   ├── crud.py         # Database operations
│   └── schemas.py      # Pydantic schemas
├── requirements.txt
├── Dockerfile
├── knowledge_base.txt
└── README.md
```
