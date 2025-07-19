from fastapi import FastAPI
from .routes import router

app = FastAPI(title="FAQ-RAG Service")
app.include_router(router)
