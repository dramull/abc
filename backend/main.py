from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.agents import router as agents_router
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ABC Multi-Agent Framework",
    description="World-class multi-agent framework with optimized UX",
    version="1.0.0"
)

# CORS middleware for frontend communication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
logger.info(f"Configuring CORS for origins: {allowed_origins}")

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
    logger.info("Health check requested")
    return {"status": "healthy", "service": "abc-multiagent-framework"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)