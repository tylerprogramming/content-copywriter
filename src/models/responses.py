"""
Response models for API endpoints
"""

from pydantic import BaseModel
from typing import Optional, List


class PostResponse(BaseModel):
    """Response model for post publishing"""
    success: bool
    platform: str
    submission_id: str
    message: str
    scheduled_time: Optional[str] = None


class MediaUploadResponse(BaseModel):
    """Response model for media uploads"""
    success: bool
    media_url: str
    message: str


class BulkPostResponse(BaseModel):
    """Response model for bulk publishing"""
    success: bool
    results: List[PostResponse]
    summary: dict
