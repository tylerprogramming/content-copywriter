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

print(f"🔍 DEBUG: Current working directory: {os.getcwd()}")
print(f"🔍 DEBUG: Base directory (main.py location): {BASE_DIR}")
print(f"🔍 DEBUG: .env file path: {ENV_PATH}")
print(f"🔍 DEBUG: .env file exists: {ENV_PATH.exists()}")

# Load .env with explicit path
load_dotenv(dotenv_path=ENV_PATH)

# Check if token is loaded
apify_token = os.getenv("APIFY_API_TOKEN")
print(f"🔍 DEBUG: APIFY_API_TOKEN loaded: {bool(apify_token)}")
if apify_token:
    print(f"🔍 DEBUG: Token preview: {apify_token[:20]}...")
else:
    print("⚠️  DEBUG: APIFY_API_TOKEN is None or empty!")

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
