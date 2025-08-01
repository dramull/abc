from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.agents import router as agents_router
import os

app = FastAPI(
    title="ABC Multi-Agent Framework",
    description="World-class multi-agent framework with optimized UX",
    version="1.0.0"
)

# CORS middleware for frontend communication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ABC Multi-Agent Framework API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "abc-multiagent-framework"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)