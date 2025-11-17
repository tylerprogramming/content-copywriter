"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TextPostRequest(BaseModel):
    """Request model for text-only posts"""
    platform: str = Field(..., description="Platform name (tiktok, instagram, linkedin, facebook, twitter, youtube, bluesky, pinterest, threads)")
    text: str = Field(..., description="Post text content")
    scheduled_time: Optional[datetime] = Field(None, description="Optional: Schedule post for future time (ISO 8601 format)")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "linkedin",
                "text": "Check out this amazing content!",
                "scheduled_time": None
            }
        }


class MediaPostRequest(BaseModel):
    """Request model for posts with media (after media is uploaded)"""
    platform: str = Field(..., description="Platform name")
    text: str = Field(..., description="Post text content")
    media_url: str = Field(..., description="Blotato media URL (from /media/upload endpoint)")
    scheduled_time: Optional[datetime] = Field(None, description="Optional: Schedule post for future time")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "instagram",
                "text": "Check out this video!",
                "media_url": "https://cdn.blotato.com/media/abc123.mp4",
                "scheduled_time": None
            }
        }


class BulkPostRequest(BaseModel):
    """Request model for publishing to multiple platforms at once"""
    platforms: List[str] = Field(..., description="List of platform names")
    text: str = Field(..., description="Post text content (same for all platforms)")
    media_url: Optional[str] = Field(None, description="Optional: Blotato media URL for media posts")
    scheduled_time: Optional[datetime] = Field(None, description="Optional: Schedule posts for future time")

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": ["linkedin", "twitter", "facebook"],
                "text": "Check out this content!",
                "media_url": None,
                "scheduled_time": None
            }
        }
