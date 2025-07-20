import logging
from fastapi import FastAPI
from .routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(title="FAQ-RAG Service")
app.include_router(router)

# Simple startup logging
logger.info("FAQ-RAG Service starting up...")
