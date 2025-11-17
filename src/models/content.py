"""
Content generation request and response models
"""

from pydantic import BaseModel, Field
from typing import Optional


class ContentGenerationRequest(BaseModel):
    """Request model for AI content generation"""
    platform: str = Field(
        ...,
        description="Target platform (youtube, linkedin, instagram, tiktok)"
    )
    input_text: str = Field(
        ...,
        description="Input text/topic to generate content from",
        min_length=10
    )
    youtube_url: Optional[str] = Field(
        None,
        description="Optional YouTube video URL to extract transcript and use as context"
    )
    additional_context: Optional[str] = Field(
        None,
        description="Optional additional context or specific requirements"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "linkedin",
                "input_text": "How AI agents are revolutionizing customer service by automating 80% of support tickets",
                "youtube_url": "https://youtu.be/NhwKQ7GwGq8",
                "additional_context": "Focus on small business benefits"
            }
        }


class ContentGenerationResponse(BaseModel):
    """Response model for AI content generation"""
    success: bool
    platform: str
    title: str
    text: str
    character_count: int
    message: str
    video_metadata: Optional[dict] = Field(
        None,
        description="Video metadata if YouTube URL was provided"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "platform": "linkedin",
                "title": "AI Agents Are Transforming Customer Service",
                "text": "80% of support tickets can now be automated...\n\n👉 Faster response times\n👉 Lower operational costs\n👉 24/7 availability\n\n#ai #aiautomation #automation #aiagent",
                "character_count": 245,
                "message": "Content generated successfully",
                "video_metadata": {
                    "title": "OpenAI AgentKit Full Beginner Course",
                    "channel_name": "Tyler AI",
                    "view_count": 6906,
                    "duration": "00:28:16"
                }
            }
        }
