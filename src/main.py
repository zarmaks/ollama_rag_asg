import logging
from fastapi import FastAPI, HTTPException
from .routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="FAQ-RAG Service")
app.include_router(router)


@app.get("/", include_in_schema=False)
def read_root():
    """
    Root endpoint providing basic service information.

    Returns:
        Dictionary with service status and available endpoints
    """
    try:
        logger.info("Root endpoint accessed")
        return {
            "message": "FAQ-RAG Service is running",
            "endpoints": ["/ask", "/history"],
            "status": "active",
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Simple startup logging
logger.info("FAQ-RAG Service starting up...")
