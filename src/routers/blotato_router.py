"""
Blotato-related API endpoints

Handles carousel generation, media uploads, and social media publishing via Blotato
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Optional
import base64

from src.services.publishing_service import PublishingService
from src.services.ai_content_service import AIContentService
from src.blotato.client import BlotatoClient
from src.config import config

from src.models.requests import TextPostRequest, MediaPostRequest, BulkPostRequest
from src.models.responses import PostResponse, MediaUploadResponse, BulkPostResponse
from src.models.content import ContentGenerationRequest, ContentGenerationResponse
from src.models.carousel import (
    CarouselRequest, CarouselResponse, TemplateListResponse,
    VideoStatusResponse, CarouselPostRequest, CarouselPostResponse,
    MultiPlatformCarouselRequest, MultiPlatformCarouselResponse
)
from src.blotato.models import MediaUploadFromUrlRequest, MediaUploadFromUrlResponse
from src.utils.url_converter import convert_url_for_upload

# Initialize router
router = APIRouter(
    prefix="",
    tags=["Blotato Publishing"]
)

# Initialize services
publishing_service = PublishingService()
ai_content_service = AIContentService()
blotato_client = BlotatoClient()


# ==================== Helper Functions ====================

def get_account_id(platform: str) -> str:
    """Get account ID for platform from config"""
    account_ids = config.PLATFORM_ACCOUNT_IDS

    if platform.lower() not in account_ids:
        raise ValueError(
            f"Platform '{platform}' not configured. Please add {platform.upper()}_ACCOUNT_ID to .env file"
        )

    return account_ids[platform.lower()]


def validate_platform(platform: str) -> str:
    """Validate platform is supported"""
    platform = platform.lower()
    supported = config.SUPPORTED_PLATFORMS

    if platform not in supported:
        raise ValueError(
            f"Unsupported platform: {platform}. Supported: {', '.join(supported)}"
        )

    return platform


# ==================== Content Generation ====================

@router.post("/content/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    Generate AI-powered, platform-specific social media content

    Takes your input text and creates optimized content for the target platform
    using AI. Each platform has custom prompts for optimal engagement.

    **Supported Platforms:**
    - **youtube** or **youtube_shorts**: YouTube Shorts captions
    - **linkedin**: Professional LinkedIn posts
    - **instagram**: Instagram captions for posts/reels
    - **tiktok**: TikTok video captions

    **Parameters:**
    - **platform**: Target platform
    - **input_text**: Your topic, idea, or raw content (min 10 characters)
    - **youtube_url**: Optional YouTube video URL to extract transcript and use as context
    - **additional_context**: Optional context or specific requirements

    **Example (with YouTube video):**
    ```json
    {
      "platform": "linkedin",
      "input_text": "Key insights from my latest video on AI automation",
      "youtube_url": "https://youtu.be/NhwKQ7GwGq8",
      "additional_context": "Focus on actionable tips for beginners"
    }
    ```

    **Example (without video):**
    ```json
    {
      "platform": "linkedin",
      "input_text": "AI agents can automate 80% of customer support tickets",
      "additional_context": "Focus on benefits for small businesses"
    }
    ```
    """
    try:
        # Validate platform for content generation
        if not ai_content_service.validate_platform(request.platform):
            supported = ", ".join(ai_content_service.get_supported_platforms())
            raise ValueError(
                f"Platform '{request.platform}' not supported for content generation. Supported: {supported}"
            )

        # Extract video transcript if YouTube URL provided
        video_transcript = None
        video_metadata = None

        if request.youtube_url:
            # Import here to avoid circular dependency
            from src.services.video_transcription_service import VideoTranscriptionService
            import os

            apify_token = os.getenv("APIFY_API_TOKEN")
            if not apify_token:
                raise HTTPException(
                    status_code=503,
                    detail="Video transcription service not available. Set APIFY_API_TOKEN environment variable."
                )

            video_transcription_service = VideoTranscriptionService(apify_api_token=apify_token)

            # Extract transcript using Apify
            result = video_transcription_service.extract_youtube_transcript(request.youtube_url)

            if result and result.get("transcript"):
                video_transcript = result["transcript"]
                video_metadata = {
                    "title": result.get("title"),
                    "channel_name": result.get("channel_name"),
                    "view_count": result.get("view_count"),
                    "likes": result.get("likes"),
                    "duration": result.get("duration"),
                    "video_id": result.get("video_id")
                }
            else:
                raise ValueError(f"Failed to extract transcript from YouTube video: {request.youtube_url}")

        # Generate content
        content = ai_content_service.generate_content(
            platform=request.platform,
            input_text=request.input_text,
            video_transcript=video_transcript,
            additional_context=request.additional_context
        )

        # Convert to API response
        return ContentGenerationResponse(
            success=True,
            platform=content.platform,
            title=content.title,
            text=content.text,
            character_count=content.character_count,
            message=f"Content generated successfully for {request.platform}",
            video_metadata=video_metadata
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


# ==================== Carousel Endpoints ====================

@router.post("/carousel/generate", response_model=CarouselResponse)
async def generate_carousel(request: CarouselRequest):
    """
    Generate a carousel post using Blotato templates

    Creates visual carousel posts (tweet cards, quote slides, etc.) using Blotato's
    template rendering system. Perfect for creating engaging multi-slide content.

    **Parameters:**
    - **inputs**: Template inputs (theme, quotes, profile info, etc.)
    - **templateId**: Blotato template ID to use
    - **render**: Whether to render immediately (default: true)
    - **isDraft**: Save as draft instead of publishing (default: false)

    **Example:**
    ```json
    {
      "inputs": {
        "theme": "light",
        "handle": "tylerreedai",
        "quotes": [
          "CrewAI lets multiple AI agents work together.",
          "Define Agents (who), Tasks (what), Tools (how).",
          "Start small, log and test, then scale."
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

    **Common Use Cases:**
    - Quote carousels for educational content
    - Tweet thread visualizations
    - Step-by-step tutorials
    - Key takeaways from longer content

    **Templates:**
    - Tweet Card: `/base/v2/tweet-card/ba413be6-a840-4e60-8fd6-0066d3b427df/v1`
    - (More templates available in Blotato dashboard)
    """
    try:
        # Convert Pydantic model to dict for Blotato API
        inputs_dict = request.inputs.model_dump()

        # Generate carousel via Blotato
        blotato_response = blotato_client.generate_carousel(
            inputs=inputs_dict,
            template_id=request.templateId,
            render=request.render,
            is_draft=request.isDraft
        )

        # Extract relevant data from response
        video_url = blotato_response.get("videoUrl") or blotato_response.get("url")
        render_id = blotato_response.get("renderId") or blotato_response.get("id")

        return CarouselResponse(
            success=True,
            video_url=video_url,
            render_id=render_id,
            template_id=request.templateId,
            slides_count=len(request.inputs.quotes),
            message=f"Carousel generated successfully with {len(request.inputs.quotes)} slides",
            blotato_response=blotato_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carousel generation failed: {str(e)}")


@router.get("/carousel/templates", response_model=TemplateListResponse)
async def list_carousel_templates(
    fields: Optional[str] = None,
    search: Optional[str] = None,
    id: Optional[str] = None
):
    """
    List all available Blotato carousel templates

    Returns a list of templates you can use with the carousel generation endpoint.
    Each template has different input parameters and visual styles.

    **Query Parameters:**
    - **fields** (optional): Comma-separated list of fields to include
      - Default: `id,title,description`
      - Full details: `id,title,description,inputs`
      - Example: `fields=id,title,description,inputs`

    - **search** (optional): Search regex term to filter templates
      - Filter by title or description
      - Example: `search=tweet` or `search=real estate`

    - **id** (optional): Get a specific template by ID
      - Example: `id=/base/v2/tweet-card/9714ae5c-7e6b-4878-be4a-4b1ba5d0cd66/v1`

    **Examples:**

    1. **List all templates (basic info):**
       ```
       GET /carousel/templates
       ```

    2. **List templates with full input specifications:**
       ```
       GET /carousel/templates?fields=id,title,description,inputs
       ```

    3. **Search for tweet-related templates:**
       ```
       GET /carousel/templates?search=tweet
       ```

    4. **Get a specific template:**
       ```
       GET /carousel/templates?id=/base/v2/tweet-card/.../v1
       ```

    **Response includes:**
    - Template ID (use this in carousel generation)
    - Title and description
    - Input parameters (if fields=inputs included)
    - Specifications for each template
    """
    try:
        # Fetch templates from Blotato
        blotato_response = blotato_client.list_templates(
            fields=fields,
            search=search,
            template_id=id
        )

        items = blotato_response.get("items", [])

        return TemplateListResponse(
            success=True,
            count=len(items),
            items=items,
            message=f"Retrieved {len(items)} template(s)"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/carousel/video/{video_id}", response_model=VideoStatusResponse)
async def get_carousel_video_status(video_id: str):
    """
    Get a single video by its ID

    Retrieves the video by its ID. This is useful for polling after creating a video
    programmatically to check its status and get the final media URL.

    **Path Parameters:**
    - **video_id**: The video ID (e.g., "123e4567-e89b-12d3-a456-426614174000")

    **Use Case:**
    After generating a carousel with `POST /carousel/generate`, you receive a `render_id`.
    Use this endpoint to poll the video status until it's completed.

    **Example Workflow:**
    ```python
    # 1. Generate carousel
    response = requests.post("/carousel/generate", json={...})
    render_id = response.json()["render_id"]

    # 2. Poll for completion
    import time
    while True:
        status = requests.get(f"/carousel/video/{render_id}")
        if status.json()["status"] == "completed":
            video_url = status.json()["media_url"]
            print(f"Video ready: {video_url}")
            break
        time.sleep(2)  # Wait 2 seconds before checking again
    ```

    **Response Statuses:**
    - **completed**: Video is ready, `media_url` field contains the download link
    - **processing**: Video is still being rendered
    - **failed**: Video generation failed
    """
    try:
        # Fetch video from Blotato
        blotato_response = blotato_client.get_video(video_id)

        item = blotato_response.get("item", {})

        return VideoStatusResponse(
            success=True,
            id=item.get("id", video_id),
            status=item.get("status", "unknown"),
            created_at=item.get("createdAt"),
            media_url=item.get("mediaUrl"),
            message=f"Video status: {item.get('status', 'unknown')}",
            item=item
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch video: {str(e)}")


@router.post("/carousel/publish", response_model=CarouselPostResponse)
async def publish_carousel_post(request: CarouselPostRequest):
    """
    Publish a carousel post to social media with optional scheduling

    Takes media URLs (from carousel generation or media upload) and publishes
    them as a carousel post to the specified platform.

    **Supported Platforms:**
    - Instagram (carousel/reel)
    - TikTok (with additional options)
    - LinkedIn
    - Twitter
    - Facebook

    **Basic Example:**
    ```json
    {
      "platform": "instagram",
      "account_id": "28",
      "text": "Check out this carousel!",
      "media_urls": ["https://url1.jpg", "https://url2.jpg"]
    }
    ```

    **Scheduled Example:**
    ```json
    {
      "platform": "instagram",
      "account_id": "28",
      "text": "Scheduled carousel post",
      "media_urls": ["https://url1.jpg"],
      "scheduled_time": "2025-01-08T15:00:00Z"
    }
    ```

    **TikTok Example:**
    ```json
    {
      "platform": "tiktok",
      "account_id": "199",
      "text": "My TikTok carousel",
      "media_urls": ["https://url1.jpg"],
      "tiktok_title": "Video Title",
      "tiktok_privacy_level": "PUBLIC_TO_EVERYONE"
    }
    ```
    """
    try:
        # Build target configuration based on platform
        target = {"targetType": request.platform}

        # Add TikTok-specific fields if applicable
        if request.platform == "tiktok":
            if request.tiktok_title:
                target["title"] = request.tiktok_title
            target["privacyLevel"] = request.tiktok_privacy_level or "PUBLIC_TO_EVERYONE"
            target["autoAddMusic"] = request.tiktok_auto_add_music
            target["isDraft"] = request.tiktok_is_draft
            target["disabledComments"] = False
            target["disabledDuet"] = False
            target["disabledStitch"] = False
            target["isBrandedContent"] = False
            target["isYourBrand"] = False
            target["isAiGenerated"] = False

        # Build post payload
        payload = {
            "post": {
                "accountId": request.account_id,
                "content": {
                    "text": request.text,
                    "platform": request.platform,
                    "mediaUrls": request.media_urls
                },
                "target": target
            },
            "useNextFreeSlot": request.use_next_free_slot
        }

        # Add scheduled time if provided
        if request.scheduled_time:
            payload["scheduledTime"] = request.scheduled_time

        # Make request to Blotato
        response_data = blotato_client._make_request(
            "POST",
            "/posts",
            json=payload
        )

        return CarouselPostResponse(
            success=True,
            post_submission_id=response_data.get("postSubmissionId"),
            platform=request.platform,
            scheduled_time=request.scheduled_time,
            message=f"Carousel post {'scheduled' if request.scheduled_time else 'published'} successfully to {request.platform}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish carousel post: {str(e)}")


@router.post("/carousel/publish-multi", response_model=MultiPlatformCarouselResponse)
async def publish_carousel_multi_platform(request: MultiPlatformCarouselRequest):
    """
    Publish carousel to multiple platforms simultaneously

    Publishes the same carousel content to multiple social media platforms
    with a single request. Automatically transforms the payload for each platform.

    **Supported Platforms:** instagram, linkedin, tiktok

    **Example:**
    ```json
    {
      "platforms": ["instagram", "linkedin", "tiktok"],
      "account_ids": {
        "instagram": "28",
        "linkedin": "45",
        "tiktok": "199"
      },
      "text": "Check out this carousel! #AI #Automation",
      "media_urls": [
        "https://database.blotato.io/.../image1.jpg",
        "https://database.blotato.io/.../image2.jpg"
      ],
      "scheduled_time": "2025-01-08T15:00:00Z",
      "tiktok_title": "My Carousel Video"
    }
    ```

    **Response includes:**
    - Individual results for each platform
    - Success/failure counts
    - Submission IDs for each platform
    """
    try:
        results = []
        successful = 0
        failed = 0

        # Publish to each platform
        for platform in request.platforms:
            # Get account ID for this platform
            account_id = request.account_ids.get(platform)

            if not account_id:
                results.append({
                    "platform": platform,
                    "success": False,
                    "error": f"No account_id provided for {platform}",
                    "post_submission_id": None
                })
                failed += 1
                continue

            # Build target configuration for this platform
            target = {"targetType": platform}

            # Add TikTok-specific fields
            if platform == "tiktok":
                if request.tiktok_title:
                    target["title"] = request.tiktok_title
                target["privacyLevel"] = request.tiktok_privacy_level or "PUBLIC_TO_EVERYONE"
                target["autoAddMusic"] = True
                target["isDraft"] = False
                target["disabledComments"] = False
                target["disabledDuet"] = False
                target["disabledStitch"] = False
                target["isBrandedContent"] = False
                target["isYourBrand"] = False
                target["isAiGenerated"] = False

            # Build post payload
            payload = {
                "post": {
                    "accountId": account_id,
                    "content": {
                        "text": request.text,
                        "platform": platform,
                        "mediaUrls": request.media_urls
                    },
                    "target": target
                },
                "useNextFreeSlot": request.use_next_free_slot
            }

            # Add scheduled time if provided
            if request.scheduled_time:
                payload["scheduledTime"] = request.scheduled_time

            # Make request to Blotato
            try:
                response_data = blotato_client._make_request(
                    "POST",
                    "/posts",
                    json=payload
                )

                results.append({
                    "platform": platform,
                    "success": True,
                    "post_submission_id": response_data.get("postSubmissionId"),
                    "scheduled_time": request.scheduled_time,
                    "message": f"Published successfully to {platform}"
                })
                successful += 1

            except Exception as platform_error:
                results.append({
                    "platform": platform,
                    "success": False,
                    "error": str(platform_error),
                    "post_submission_id": None
                })
                failed += 1

        # Determine overall success
        all_success = failed == 0

        return MultiPlatformCarouselResponse(
            success=all_success,
            results=results,
            total_platforms=len(request.platforms),
            successful_platforms=successful,
            failed_platforms=failed,
            message=f"Published to {successful}/{len(request.platforms)} platforms successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish multi-platform carousel: {str(e)}")


# ==================== Media Upload Endpoints ====================

@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    """
    Upload media file (image/video) to Blotato

    Returns a media URL that can be used in /posts/media endpoint

    - **file**: Media file to upload (image or video)
    """
    try:
        # Read file content
        file_content = await file.read()

        # Determine MIME type from file extension
        file_extension = file.filename.split('.')[-1].lower()

        mime_types = {
            'mp4': 'video/mp4',
            'mov': 'video/quicktime',
            'avi': 'video/x-msvideo',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        mime_type = mime_types.get(file_extension, 'application/octet-stream')

        # Create base64 data URL
        base64_content = base64.b64encode(file_content).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_content}"

        # Upload to Blotato
        response = blotato_client.upload_media(url=data_url)

        return MediaUploadResponse(
            success=True,
            media_url=response.url,
            message=f"Media uploaded successfully: {file.filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/media/upload-from-url", response_model=MediaUploadFromUrlResponse)
async def upload_media_from_url(request: MediaUploadFromUrlRequest):
    """
    Upload media from a URL (supports Google Drive links)

    Automatically converts Google Drive share links to direct download URLs.

    - **url**: Media URL (supports Google Drive share links)

    **Example Google Drive URL:**
    ```
    https://drive.google.com/file/d/1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq/view?usp=drive_link
    ```

    **Converts to:**
    ```
    https://drive.google.com/uc?export=download&id=1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq
    ```
    """
    try:
        original_url = request.url

        # Convert URL if it's a Google Drive link
        converted_url = convert_url_for_upload(original_url)

        # Upload to Blotato using converted URL
        response = blotato_client.upload_media(url=converted_url)

        return MediaUploadFromUrlResponse(
            success=True,
            media_url=str(response.url),
            original_url=original_url,
            converted_url=converted_url if converted_url != original_url else None,
            message=f"Media uploaded successfully from URL"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload from URL failed: {str(e)}")


# ==================== Publishing Endpoints ====================

@router.post("/posts/text", response_model=PostResponse)
async def publish_text_post(request: TextPostRequest):
    """
    Publish a text-only post to a social media platform

    - **platform**: Target platform (tiktok, instagram, linkedin, etc.)
    - **text**: Post content text
    - **scheduled_time**: Optional ISO 8601 datetime for scheduling
    """
    try:
        # Validate platform
        platform = validate_platform(request.platform)

        # Get account ID
        account_id = get_account_id(platform)

        # Publish post (no media)
        response = publishing_service.publish_post(
            account_id=account_id,
            platform=platform,
            text=request.text,
            media_urls=None,
            scheduled_time=request.scheduled_time
        )

        return PostResponse(
            success=True,
            platform=platform,
            submission_id=response.postSubmissionId,
            message=f"Post published successfully to {platform}",
            scheduled_time=request.scheduled_time.isoformat() if request.scheduled_time else None
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/posts/media", response_model=PostResponse)
async def publish_media_post(request: MediaPostRequest):
    """
    Publish a post with media to a social media platform

    Use /media/upload first to get a media URL, then use it here

    - **platform**: Target platform
    - **text**: Post content text
    - **media_url**: Blotato media URL (from /media/upload)
    - **scheduled_time**: Optional scheduling time
    """
    try:
        # Validate platform
        platform = validate_platform(request.platform)

        # Get account ID
        account_id = get_account_id(platform)

        # Publish post with media
        response = publishing_service.publish_post(
            account_id=account_id,
            platform=platform,
            text=request.text,
            media_urls=[request.media_url],
            scheduled_time=request.scheduled_time
        )

        return PostResponse(
            success=True,
            platform=platform,
            submission_id=response.postSubmissionId,
            message=f"Media post published successfully to {platform}",
            scheduled_time=request.scheduled_time.isoformat() if request.scheduled_time else None
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/posts/bulk", response_model=BulkPostResponse)
async def publish_bulk_posts(request: BulkPostRequest):
    """
    Publish the same content to multiple platforms at once

    - **platforms**: List of platforms to publish to
    - **text**: Post content (same for all platforms)
    - **media_url**: Optional media URL for all posts
    - **scheduled_time**: Optional scheduling time for all posts
    """
    results = []
    success_count = 0
    failure_count = 0

    for platform in request.platforms:
        try:
            # Validate platform
            platform = validate_platform(platform)

            # Get account ID
            account_id = get_account_id(platform)

            # Publish post
            response = publishing_service.publish_post(
                account_id=account_id,
                platform=platform,
                text=request.text,
                media_urls=[request.media_url] if request.media_url else None,
                scheduled_time=request.scheduled_time
            )

            results.append(PostResponse(
                success=True,
                platform=platform,
                submission_id=response.postSubmissionId,
                message=f"Published successfully to {platform}",
                scheduled_time=request.scheduled_time.isoformat() if request.scheduled_time else None
            ))
            success_count += 1

        except Exception as e:
            results.append(PostResponse(
                success=False,
                platform=platform,
                submission_id="",
                message=f"Failed: {str(e)}"
            ))
            failure_count += 1

    return BulkPostResponse(
        success=success_count > 0,
        results=results,
        summary={
            "total": len(request.platforms),
            "successful": success_count,
            "failed": failure_count
        }
    )
