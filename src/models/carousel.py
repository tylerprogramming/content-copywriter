"""
Carousel Post Models

Request and response models for Blotato carousel/template-based posts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class CarouselInputs(BaseModel):
    """Inputs for carousel template rendering"""

    theme: Literal["light", "dark"] = Field(
        default="light",
        description="Visual theme for the carousel"
    )

    handle: str = Field(
        ...,
        description="Social media handle (e.g., 'tylerreedai')",
        examples=["tylerreedai", "myhandle"]
    )

    quotes: List[str] = Field(
        ...,
        description="List of text quotes/slides for the carousel",
        min_length=1,
        max_length=10
    )

    verified: bool = Field(
        default=True,
        description="Show verified badge next to handle"
    )

    authorName: str = Field(
        ...,
        description="Full name of the author",
        examples=["Tyler Reed"]
    )

    aspectRatio: Literal["1:1", "4:5", "16:9"] = Field(
        default="4:5",
        description="Aspect ratio for the carousel"
    )

    profileImage: str = Field(
        ...,
        description="URL to the profile image",
        examples=["https://example.com/profile.jpg"]
    )


class CarouselRequest(BaseModel):
    """
    Request model for generating carousel posts via Blotato templates

    Generates visual carousel posts (like tweet cards, quote slides, etc.)
    using Blotato's template rendering system.

    **Example:**
    ```json
    {
      "inputs": {
        "theme": "light",
        "handle": "tylerreedai",
        "quotes": [
          "CrewAI lets multiple AI agents work together.",
          "Define Agents (who), Tasks (what), Tools (how)."
        ],
        "verified": true,
        "authorName": "Tyler Reed",
        "aspectRatio": "4:5",
        "profileImage": "https://example.com/profile.jpg"
      },
      "templateId": "/base/v2/tweet-card/ba413be6-a840-4e60-8fd6-0066d3b427df/v1",
      "render": true,
      "isDraft": false
    }
    ```
    """

    inputs: CarouselInputs = Field(
        ...,
        description="Template inputs (theme, quotes, profile info, etc.)"
    )

    render: bool = Field(
        default=True,
        description="Whether to render the template immediately"
    )

    isDraft: bool = Field(
        default=False,
        description="Save as draft instead of publishing"
    )

    templateId: str = Field(
        ...,
        description="Blotato template ID to use for rendering",
        examples=["/base/v2/tweet-card/ba413be6-a840-4e60-8fd6-0066d3b427df/v1"]
    )


class CarouselResponse(BaseModel):
    """Response model for carousel generation"""

    success: bool = Field(description="Whether generation was successful")

    video_url: Optional[str] = Field(
        None,
        description="URL to the generated carousel video/animation"
    )

    render_id: Optional[str] = Field(
        None,
        description="Blotato render ID for tracking"
    )

    template_id: str = Field(
        description="Template ID that was used"
    )

    slides_count: int = Field(
        description="Number of slides in the carousel"
    )

    message: str = Field(
        description="Status message"
    )

    blotato_response: Optional[dict] = Field(
        None,
        description="Full response from Blotato API"
    )


class TemplateListResponse(BaseModel):
    """Response model for listing available templates"""

    success: bool = Field(
        default=True,
        description="Whether the request was successful"
    )

    count: int = Field(
        description="Number of templates returned"
    )

    items: List[dict] = Field(
        description="List of template objects with id, title, description, and optionally inputs"
    )

    message: str = Field(
        description="Status message"
    )


class VideoStatusResponse(BaseModel):
    """Response model for getting video status"""

    success: bool = Field(
        default=True,
        description="Whether the request was successful"
    )

    id: str = Field(
        description="Video ID"
    )

    status: str = Field(
        description="Video status (e.g., 'completed', 'processing', 'failed')"
    )

    created_at: Optional[str] = Field(
        None,
        description="When the video was created (ISO 8601 format)"
    )

    media_url: Optional[str] = Field(
        None,
        description="URL to the generated video (available when status is 'completed')"
    )

    message: str = Field(
        description="Status message"
    )

    item: Optional[dict] = Field(
        None,
        description="Full item response from Blotato API"
    )


class CarouselPostRequest(BaseModel):
    """
    Request to publish a carousel post to social media

    **Example (Instagram):**
    ```json
    {
      "platform": "instagram",
      "account_id": "28",
      "text": "Check out this carousel!",
      "media_urls": ["https://url1.jpg", "https://url2.jpg"],
      "scheduled_time": "2025-01-08T15:00:00Z"
    }
    ```

    **Example (TikTok with options):**
    ```json
    {
      "platform": "tiktok",
      "account_id": "199",
      "text": "My carousel video!",
      "media_urls": ["https://url1.jpg"],
      "tiktok_title": "My Video Title",
      "tiktok_privacy_level": "PUBLIC_TO_EVERYONE",
      "scheduled_time": "2025-01-08T15:00:00Z"
    }
    ```
    """

    platform: Literal["instagram", "tiktok", "linkedin", "twitter", "facebook"] = Field(
        ...,
        description="Target platform"
    )

    account_id: str = Field(
        ...,
        description="Blotato account ID for the platform"
    )

    text: str = Field(
        ...,
        description="Post text/caption"
    )

    media_urls: List[str] = Field(
        ...,
        description="List of Blotato media URLs (from carousel generation or media upload)",
        min_length=1
    )

    scheduled_time: Optional[str] = Field(
        None,
        description="Schedule post for later (ISO 8601 format)",
        examples=["2025-01-08T15:00:00Z"]
    )

    use_next_free_slot: bool = Field(
        default=False,
        description="Use next available posting slot"
    )

    # TikTok-specific fields
    tiktok_title: Optional[str] = Field(
        None,
        description="TikTok video title (max 90 chars)"
    )

    tiktok_privacy_level: Optional[Literal[
        "PUBLIC_TO_EVERYONE",
        "SELF_ONLY",
        "MUTUAL_FOLLOW_FRIENDS",
        "FOLLOWER_OF_CREATOR"
    ]] = Field(
        default="PUBLIC_TO_EVERYONE",
        description="TikTok privacy level"
    )

    tiktok_auto_add_music: bool = Field(
        default=True,
        description="Auto-add music on TikTok"
    )

    tiktok_is_draft: bool = Field(
        default=False,
        description="Save as draft on TikTok"
    )


class CarouselPostResponse(BaseModel):
    """Response for carousel post publishing"""

    success: bool = Field(
        description="Whether post was published successfully"
    )

    post_submission_id: str = Field(
        description="Blotato post submission ID"
    )

    platform: str = Field(
        description="Platform where post was published"
    )

    scheduled_time: Optional[str] = Field(
        None,
        description="Scheduled time if applicable"
    )

    message: str = Field(
        description="Status message"
    )


class MultiPlatformCarouselRequest(BaseModel):
    """
    Request to publish carousel to multiple platforms at once

    **Example:**
    ```json
    {
      "platforms": ["instagram", "linkedin", "tiktok"],
      "account_ids": {
        "instagram": "28",
        "linkedin": "45",
        "tiktok": "199"
      },
      "text": "Check out this carousel!",
      "media_urls": ["https://url1.jpg", "https://url2.jpg"],
      "scheduled_time": "2025-01-08T15:00:00Z",
      "tiktok_title": "My Video Title"
    }
    ```
    """

    platforms: List[Literal["instagram", "linkedin", "tiktok"]] = Field(
        ...,
        description="List of platforms to publish to",
        min_length=1
    )

    account_ids: dict = Field(
        ...,
        description="Map of platform to account ID (e.g., {'instagram': '28', 'linkedin': '45'})"
    )

    text: str = Field(
        ...,
        description="Post text/caption (used for all platforms)"
    )

    media_urls: List[str] = Field(
        ...,
        description="List of Blotato media URLs",
        min_length=1
    )

    scheduled_time: Optional[str] = Field(
        None,
        description="Schedule post for later (ISO 8601 format) - applies to all platforms",
        examples=["2025-01-08T15:00:00Z"]
    )

    use_next_free_slot: bool = Field(
        default=False,
        description="Use next available posting slot"
    )

    # TikTok-specific (optional)
    tiktok_title: Optional[str] = Field(
        None,
        description="TikTok video title (only used if TikTok is in platforms list)"
    )

    tiktok_privacy_level: Optional[Literal[
        "PUBLIC_TO_EVERYONE",
        "SELF_ONLY",
        "MUTUAL_FOLLOW_FRIENDS",
        "FOLLOWER_OF_CREATOR"
    ]] = Field(
        default="PUBLIC_TO_EVERYONE",
        description="TikTok privacy level"
    )


class MultiPlatformCarouselResponse(BaseModel):
    """Response for multi-platform carousel publishing"""

    success: bool = Field(
        description="Whether all posts were published successfully"
    )

    results: List[dict] = Field(
        description="List of results for each platform"
    )

    total_platforms: int = Field(
        description="Total number of platforms"
    )

    successful_platforms: int = Field(
        description="Number of successful publishes"
    )

    failed_platforms: int = Field(
        description="Number of failed publishes"
    )

    message: str = Field(
        description="Overall status message"
    )
