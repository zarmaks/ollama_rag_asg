# FAQ-RAG Service

A FastAPI-based REST API service that integrates Mistral LLM via Ollama to answer user queries using a predefined knowledge base, with comprehensive query logging and retrieval functionality.

## 🎯 Project Overview

This is a production-ready FAQ assistant that implements a RAG (Retrieval-Augmented Generation) pipeline to answer customer questions using a local Mistral LLM model. The service combines semantic search with keyword matching to provide accurate, contextually relevant answers from a structured knowledge base.

**Development Approach**: This project demonstrates strategic AI tool utilization throughout the software development lifecycle, showcasing how different LLMs can be methodically employed for planning, implementation, quality assurance, and production enhancement.

### Key Features

- **REST API** with FastAPI framework
- **Mistral LLM integration** via Ollama for local, privacy-focused inference
- **Advanced RAG Implementation** with hybrid vector similarity and BM25 retrieval
- **SQLite persistence** with SQLAlchemy ORM for query/response logging
- **Docker support** for containerized deployment
- **Comprehensive logging** and error handling
- **Environment-aware configuration** (auto-detects Docker vs local development)

## 🏗️ Architecture

The service implements a sophisticated RAG pipeline that combines:

- **Semantic Search**: Vector embeddings using Ollama's `nomic-embed-text` model
- **Keyword Search**: BM25 retrieval for exact term matching  
- **Hybrid Ensemble**: Weighted combination (60% semantic, 40% keyword) for optimal results
- **Smart URL Detection**: Automatically configures Ollama endpoints for Docker or local environments

## 🛠️ Technical Stack

- **Framework**: FastAPI with async/await support
- **LLM**: Mistral via Ollama (local inference)
- **Vector Store**: ChromaDB for embeddings persistence  
- **Database**: SQLite with SQLAlchemy ORM
- **Retrieval**: LangChain with EnsembleRetriever
- **Containerization**: Docker with optimized uv package manager

## 📋 Assignment Requirements Fulfilled

This implementation meets all the specified requirements:

### ✅ REST API (FastAPI)
- **POST /ask**: Accepts queries and returns LLM-generated answers
- **GET /history**: Retrieves past queries with configurable limit (default: 10)

### ✅ LLM Integration  
- **Mistral LLM** integration via Ollama for local inference
- **RAG implementation** with semantic and keyword search
- **Context injection** with structured prompts

### ✅ Prompt Engineering
- **Factual assistant prompt** designed for accurate FAQ responses
- **Context-aware responses** using retrieved knowledge base segments
- **Fallback handling** for out-of-scope queries

### ✅ Persistence Module
- **SQLite database** with SQLAlchemy ORM
- **Query/response logging** with automatic timestamps
- **History retrieval** with configurable limits

### ✅ Bonus Features
- **Comprehensive logging** across all modules
- **Error handling** with proper HTTP status codes
- **Docker support** with production-ready Dockerfile

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama** from [ollama.com](https://ollama.com/)
2. **Pull required models**:
   ```bash
   ollama pull mistral
   ollama pull nomic-embed-text
   ```
3. **Start Ollama server** (important for Docker):
   ```powershell
   $env:OLLAMA_HOST="0.0.0.0:11434"; ollama serve
   ```

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd faq-rag-service
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Access endpoints**:
   - API Documentation: http://localhost:8000/docs
   - Service Status: http://localhost:8000/

### Docker Deployment

1. **Build the optimized image**:
   ```bash
   docker build -t faq-rag-service .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 8000:8000 --name faq-rag faq-rag-service
   ```

**Important**: Ensure Ollama is running with `OLLAMA_HOST="0.0.0.0:11434"` before starting the container.

## 📡 API Endpoints

### POST /ask
Submit a question and receive an AI-generated answer.

**Request**:
```json
{
  "question": "What is your refund policy?"
}
```

**Response**:
```json
{
  "answer": "Month-to-month plans are non-refundable, but if we miss our SLA you'll receive automatic service credits. Annual upfront plans may be cancelled within 30 days for a prorated refund minus used-month charges."
}
```

### GET /history
Retrieve previous questions and answers with timestamps.

**Query Parameters**:
- `limit`: Integer (default: 10) - Number of recent interactions to return

**Response**:
```json
[
  {
    "question": "What is your refund policy?",
    "answer": "Month-to-month plans are non-refundable...",
    "timestamp": "2025-07-22T01:30:00"
  }
]
```

**Alternative Parameter**: The API also supports `n` parameter for compatibility:
```
GET /history?n=35
```

### GET / (Root)
Service status and available endpoints.

**Response**:
```json
{
  "message": "FAQ-RAG Service is running",
  "endpoints": ["/ask", "/history"],
  "status": "active"
}
```

## 📄 Knowledge Base

The service uses a structured Q&A format stored in `data/knowledge_base.txt`:

```text
Q: What is your refund policy?
A: Month-to-month plans are non-refundable, but if we miss our SLA you'll receive automatic service credits as outlined above. Annual upfront plans may be cancelled within 30 days for a prorated refund minus used-month charges.

---

Q: How can I contact support?
A: You can reach our support team via email at support@cloudsphere.com or call our hotline at +1 800 555-0199. Our technical support hours are Monday through Friday, 9 AM to 6 PM EST.
```

### Knowledge Base Generation

The CloudSphere knowledge base was created through a strategic multi-stage AI process:

#### Stage 1: Prompt Engineering (Claude Opus 3)
Three different prompt strategies were developed and evaluated:
1. **Comprehensive coverage approach**: Broad FAQ categories with balanced complexity
2. **Customer journey mapping**: Questions organized by user lifecycle stages  
3. **Support ticket analysis**: FAQ based on common support scenarios

#### Stage 2: Content Generation (ChatGPT-3)
The selected prompt strategy was implemented to generate the final knowledge base:

```
You are creating a comprehensive FAQ knowledge base for a mid-sized technology company that provides cloud services and software solutions. Generate 25-30 FAQ pairs that cover:

1. Product information and features
2. Pricing and billing questions  
3. Technical support and troubleshooting
4. Account management and security
5. Integration and API questions
6. Service availability and maintenance
7. Data privacy and compliance
8. Refund and cancellation policies

For each FAQ pair, use this exact format:
Q: [Question that a real customer might ask]
A: [Detailed, helpful answer that provides clear guidance and next steps where appropriate]

Make the questions varied in complexity - include both simple ("What are your business hours?") and more complex technical questions.
```

This multi-stage approach demonstrates how different AI tools can be strategically combined for optimal content quality - using Claude's analytical strength for prompt design and ChatGPT's content generation capabilities for the final output.

## 🧪 Testing

### Basic Testing
```bash
# Run unit tests
pytest

# Run API tests with verbose output
pytest tests/test_api.py -v

# Run specific test modules
pytest tests/test_parser.py
pytest tests/test_rag.py
```

### Manual API Testing

Using **curl** (Linux/Mac):
```bash
# Test the ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your refund policy?"}'

# Test the history endpoint
curl http://localhost:8000/history?limit=5
```

Using **PowerShell** (Windows):
```powershell
# Test the ask endpoint
Invoke-RestMethod -Uri http://localhost:8000/ask -Method Post -ContentType "application/json" -Body '{"question": "What is your refund policy?"}'

# Test the history endpoint  
Invoke-RestMethod -Uri http://localhost:8000/history?limit=5
```

## 🏗️ Project Structure

```
faq-rag-service/
├── src/                          # Core application code
│   ├── main.py                   # FastAPI app initialization
│   ├── routes.py                 # API endpoint definitions
│   ├── models.py                 # SQLAlchemy database models
│   ├── schemas.py                # Pydantic request/response models
│   ├── database.py               # Database configuration
│   ├── crud.py                   # Database operations
│   ├── parser.py                 # Knowledge base parser
│   └── rag.py                    # RAG service implementation
├── tests/                        # Unit and integration tests
│   ├── test_api.py              # API endpoint testing
│   ├── test_parser.py           # Parser testing
│   ├── test_rag.py              # RAG service testing
│   └── conftest.py              # Pytest configuration
├── data/
│   ├── knowledge_base.txt       # FAQ knowledge base
│   └── knowledge_base_prompt.txt # Knowledge base prompts
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── pytest.ini                   # Pytest settings
└── README.md                    # This documentation
```

## 🔧 Configuration & Environment

### Environment Detection
The service automatically detects its environment and configures Ollama endpoints accordingly:

- **Local Development**: Uses `http://localhost:11434`
- **Docker Container**: Uses `http://host.docker.internal:11434`

This is handled by the `get_ollama_base_url()` function in `src/rag.py`.

### Configuration Options

**Database**:
- SQLite database automatically created as `./test.db`
- Vector store persisted in `./chroma_db/`

**Retrieval Parameters**:
- Semantic retriever: Top 3 results
- BM25 retriever: Top 3 results  
- Ensemble weights: 60% semantic, 40% keyword

**LLM Settings**:
- Model: `mistral` 
- Temperature: 0.3 (for consistent responses)
- Embedding model: `nomic-embed-text`

## 🐳 Docker Optimization

The Dockerfile includes several optimizations:

### Build Performance
- **uv package manager**: 30% faster installations compared to pip
- **Multi-layer caching**: Optimizes rebuild times
- **Minimal base image**: Python 3.11-slim for reduced size

### Build Comparison
- **With uv**: ~38.5s build time, 710MB image
- **With pip**: ~53.6s build time, 862MB image

### Production Features
- **Non-root user**: Security best practice
- **Health checks**: Built-in endpoint monitoring
- **Environment variable support**: Flexible configuration
- **Proper signal handling**: Graceful shutdowns

## 🤖 Strategic AI-Assisted Development Workflow

This project demonstrates a methodical approach to leveraging multiple AI tools throughout the software development lifecycle, showcasing how different LLMs can be strategically employed for their unique strengths.

### Phase 1: Learning & Architecture Planning (Claude Opus 3)
**Initial consultation and education approach:**
- **Day-by-day development plan**: Created a structured timeline breaking down RAG system components
- **Interactive learning sessions**: In-depth discussions about FastAPI endpoints, CRUD operations, and database design patterns
- **RAG methodology analysis**: Comprehensive evaluation of different retrieval approaches with practical examples
- **Architecture decision making**: Guided comparison of vector search vs. hybrid approaches

*This phase was crucial for building deep understanding rather than just copying code - similar to working with a senior architect who explains the 'why' behind each decision.*

### Phase 2: Implementation & Code Development (ChatGPT-4 Mini)
**Core development and function completion:**
- **Function implementation**: Real-time assistance in completing class methods and API handlers
- **Code logic refinement**: Interactive debugging and optimization of algorithmic components
- **Integration patterns**: Seamless connection between FastAPI routes, database operations, and RAG pipeline
- **Type hint completion**: Ensuring production-ready code with proper typing throughout

*ChatGPT-4 Mini proved excellent for rapid iteration during active coding sessions, providing immediate context-aware suggestions.*

### Phase 3: Integration & Quality Assurance (GitHub Copilot with Claude Sonnet 3.5)
**Production readiness and comprehensive testing:**
- **Agent-based code review**: Automated identification and resolution of compatibility issues between modules
- **Test suite generation**: Complete pytest implementation covering unit tests, integration tests, and API endpoints
- **Documentation creation**: Professional README structure with comprehensive API documentation
- **Docker containerization**: Production-ready Dockerfile with optimization best practices
- **Configuration management**: Environment detection and proper .gitignore setup

*The agent-based approach was particularly powerful for systematic code quality improvements across the entire codebase.*

### Phase 4: Production Enhancement (ChatGPT Codex)
**Repository-wide optimization via GitHub integration:**
- **Codebase analysis**: Direct repository import for comprehensive code review
- **Logging enhancement**: Strategic placement of logging statements throughout the application
- **Error handling improvements**: Robust exception handling with proper HTTP status codes
- **Pull request workflow**: Professional code review process with detailed improvement suggestions

*First experience with Codex demonstrated the power of repository-level analysis for identifying patterns and improvements.*

### Knowledge Base Creation Workflow
**Multi-stage content generation process:**
- **Prompt engineering (Claude Opus 3)**: Created three different approaches for FAQ generation
- **Content creation (ChatGPT-3)**: Selected optimal prompt strategy and generated comprehensive CloudSphere knowledge base
- **Quality validation**: Ensured realistic SaaS company scenarios with appropriate technical depth

### Strategic AI Tool Selection Rationale

| Development Phase | Primary Tool | Rationale |
|------------------|--------------|-----------|
| **Planning & Learning** | Claude Opus 3 | Superior explanatory capabilities and architectural thinking |
| **Active Coding** | ChatGPT-4 Mini | Fast, context-aware code completion during development |
| **Quality & Integration** | GitHub Copilot + Sonnet 3.5 | Agent-based systematic improvements across entire codebase |
| **Production Polish** | ChatGPT Codex | Repository-level analysis and enterprise-grade enhancements |

### Key Productivity Insights
- **Tool specialization**: Each AI excels in specific development phases
- **Learning vs. doing**: Use conversational AI for education, coding AI for implementation
- **Quality at scale**: Agent-based tools excel at systematic improvements across large codebases
- **Repository integration**: Modern AI tools can understand entire project context for better suggestions

This methodical approach to AI tool utilization resulted in faster development cycles while maintaining code quality and comprehensive understanding of the implemented solutions.

## 📊 Performance Considerations

### Response Times
- Average response time: 5-30 seconds (depending on query complexity)
- First query may be slower due to model loading
- Subsequent queries benefit from warm model cache

### Scalability
- **Stateless design**: Horizontal scaling ready
- **Database connection pooling**: Efficient resource usage
- **Persistent vector store**: Faster startup after initial indexing
- **Configurable retrieval**: Tunable performance vs accuracy

### Memory Usage
- **Model caching**: Ollama handles efficient model memory management
- **Vector store**: ChromaDB provides optimized similarity search
- **Database**: SQLite suitable for moderate traffic loads

## 🔒 Security & Production Readiness

### Input Validation
- **Pydantic schemas**: Automatic request validation
- **SQL injection prevention**: SQLAlchemy ORM protection
- **Error sanitization**: Safe error messages without internal details

### Monitoring & Observability
- **Structured logging**: Configurable levels across all components
- **Request tracking**: Full request/response logging for debugging
- **Health checks**: Built-in service status monitoring
- **Performance metrics**: Response time and error rate tracking

### Deployment Considerations
- **Environment variables**: Externalized configuration
- **Graceful shutdowns**: Proper SIGTERM handling
- **Resource limits**: Container memory and CPU constraints
- **Network security**: Configurable CORS and allowed origins

## 🚦 Troubleshooting

### Common Issues

**1. "Connection refused" errors**:
- Ensure Ollama is running: `ollama list` should show models
- For Docker: Start Ollama with `$env:OLLAMA_HOST="0.0.0.0:11434"; ollama serve`
- Check firewall settings if running in containers

**2. "ModuleNotFoundError: No module named 'rank_bm25'"**:
- This dependency is included in requirements.txt
- Rebuild Docker image if using containers

**3. Slow response times**:
- First query loads the model (normal behavior)  
- Check system resources during LLM inference
- Consider using faster embedding models for production

**4. Database errors**:
- Database is auto-created on first run
- Check write permissions in application directory
- Review logs for SQLAlchemy connection issues

### Debugging Commands
```bash
# Check Ollama status
ollama list
curl http://localhost:11434/api/tags

# View service logs  
docker logs faq-rag-service

# Test database connection
python -c "from src.database import engine; print(engine.url)"

# Verify knowledge base parsing
python -c "from src.parser import parse_knowledge_base; docs = parse_knowledge_base(); print(f'Loaded {len(docs)} documents')"
```

## 📈 Future Enhancements

### Potential Improvements
- **Multiple knowledge bases**: Support for domain-specific FAQ sets
- **User authentication**: Request tracking and rate limiting
- **Advanced analytics**: Query analysis and knowledge gap identification
- **Caching layer**: Redis for frequent query responses
- **Batch processing**: Bulk query handling for enterprise use

### Scaling Considerations
- **Horizontal scaling**: Load balancer with multiple instances
- **Database upgrade**: PostgreSQL for production workloads
- **Model optimization**: Fine-tuned models for specific domains
- **CDN integration**: Static asset delivery optimization

---

## 📄 License

This project is developed as a demonstration of modern RAG system implementation and FastAPI best practices for educational and evaluation purposes.

---

**Note**: This implementation demonstrates production-ready patterns for RAG systems, including hybrid retrieval, comprehensive error handling, and scalable architecture suitable for real-world deployment.
