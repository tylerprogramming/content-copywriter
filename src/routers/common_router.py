"""
Common API endpoints

Shared endpoints for health check, platform info, etc.
"""

from fastapi import APIRouter

from src.config import config

# Initialize router
router = APIRouter(
    tags=["Common"]
)


@router.get("/")
async def root():
    """API health check and info"""
    return {
        "name": "Blotato Social Media API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_content": "POST /content/generate",
            "skool_post_generate": "POST /skool/post/generate",
            "carousel_generate": "POST /carousel/generate",
            "carousel_templates": "GET /carousel/templates",
            "carousel_video_status": "GET /carousel/video/{id}",
            "carousel_publish": "POST /carousel/publish",
            "carousel_publish_multi": "POST /carousel/publish-multi",
            "text_post": "POST /posts/text",
            "media_upload": "POST /media/upload",
            "media_upload_url": "POST /media/upload-from-url",
            "media_post": "POST /posts/media",
            "bulk_post": "POST /posts/bulk",
            "platforms": "GET /platforms"
        }
    }


@router.get("/platforms")
async def get_platforms():
    """Get list of supported platforms and their configuration status"""
    account_ids = config.PLATFORM_ACCOUNT_IDS

    platforms_status = {}
    for platform in config.SUPPORTED_PLATFORMS:
        platforms_status[platform] = {
            "configured": platform in account_ids,
            "account_id": account_ids.get(platform, None)
        }

    return {
        "supported_platforms": config.SUPPORTED_PLATFORMS,
        "platforms_status": platforms_status
    }
