import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from rag_engine import rag_engine

app = FastAPI(
    title="BOCHE Chemmanur Credits RAG Chatbot API",
    description="FAISS-backed RAG engine for Chemmanur Credits and Investments Limited",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "rag_ready": rag_engine.is_ready,
        "vector_count": rag_engine.index.ntotal if rag_engine.is_ready else 0
    }

@app.post("/api/chat")
def chat_endpoint(request: QueryRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    if not rag_engine.is_ready:
        # Fallback to reload if ready file exists
        rag_engine.load_index()
    
    result = rag_engine.generate_response(request.question)
    return {
        "question": request.question,
        "answer": result["answer"],
        "citations": result["citations"]
    }

@app.post("/api/reindex")
def reindex_endpoint():
    try:
        import ingest
        ingest.build_faiss_index()
        rag_engine.load_index()
        return {"status": "success", "message": "FAISS Index rebuilt and reloaded successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for web UI
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
