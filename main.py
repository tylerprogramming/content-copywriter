"""
FastAPI server for Blotato social media publishing

Main application with routes organized into routers.
"""

from fastapi import FastAPI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load .env with explicit path
load_dotenv(dotenv_path=ENV_PATH)

if not os.getenv("APIFY_API_TOKEN"):
    print("⚠️  APIFY_API_TOKEN is not set; requests with a youtube_url will return 503.")

# Import routers
from src.routers import common_router, skool_router, blotato_router, automation_router

# Initialize FastAPI app
app = FastAPI(
    title="Blotato Social Media API",
    description="API for publishing content to multiple social media platforms",
    version="1.0.0"
)

# Include routers
app.include_router(common_router)
app.include_router(skool_router)
app.include_router(blotato_router)
app.include_router(automation_router)


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
