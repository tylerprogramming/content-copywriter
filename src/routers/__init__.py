"""
API Routers

Organizes API endpoints into logical groups:
- common_router: Health check, platform info
- skool_router: Skool community post generation
- blotato_router: Carousel, media upload, social publishing
- automation_router: Workflow automations (Drive to Blotato, transcription)
"""

from src.routers.common_router import router as common_router
from src.routers.skool_router import router as skool_router
from src.routers.blotato_router import router as blotato_router
from src.routers.automation_router import router as automation_router

__all__ = ["common_router", "skool_router", "blotato_router", "automation_router"]
