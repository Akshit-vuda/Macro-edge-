#!/usr/bin/env python3
"""
MacroEdge - AI-Powered Macro Trading Intelligence Platform
Main entry point.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import services
from backend.services.database import DatabaseService
from backend.services.news_intelligence import NewsScraper, SentimentAnalyzer
from backend.services.claude_brain import ClaudeSupervisor
from config.settings import DATABASE_URL

# Initialize services
db = DatabaseService(DATABASE_URL)
news_scraper = NewsScraper()
sentiment_analyzer = SentimentAnalyzer()
claude_supervisor = ClaudeSupervisor()
scheduler = AsyncIOScheduler()

# Create FastAPI app
app = FastAPI(
    title="MacroEdge API",
    description="AI-Powered Macro Trading Intelligence Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("Starting MacroEdge...")
    
    # Initialize database
    await db.init_tables()
    logger.info("Database initialized")
    
    # Load ML models (if available)
    try:
        await sentiment_analyzer.load_model()
        logger.info("ML models loaded")
    except Exception as e:
        logger.warning(f"ML models not loaded: {e}")
    
    # Schedule jobs
    scheduler.add_job(
        news_scrape_job,
        'interval',
        hours=1,
        id='news_scrape'
    )
    scheduler.start()
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down MacroEdge...")
    scheduler.shutdown()
    await db.close()


# Import and include routers
from backend.api.routes import router as api_router
app.include_router(api_router, prefix="/api/v1")


# Scheduled jobs
async def news_scrape_job():
    """Periodic news scraping."""
    logger.info("Running scheduled news scrape...")


# Root endpoint
@app.get("/")
async def root():
    """API root."""
    return {
        "name": "MacroEdge API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "database": "connected"
    }


def main():
    """Run the application."""
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )


if __name__ == "__main__":
    main()