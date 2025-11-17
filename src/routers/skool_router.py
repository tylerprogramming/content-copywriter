"""
Skool-related API endpoints

Handles Skool community post generation
"""

from fastapi import APIRouter, HTTPException

from src.services.skool_content_service import SkoolContentService
from src.models.skool import SkoolPostRequest, SkoolPostResponse

# Initialize router
router = APIRouter(
    prefix="/skool",
    tags=["Skool Posts"]
)

# Initialize service
skool_content_service = SkoolContentService()


@router.post("/post/generate", response_model=SkoolPostResponse)
async def generate_skool_post(request: SkoolPostRequest):
    """
    Generate day-specific Skool community posts

    Automatically detects the current day of week and uses the appropriate prompt template.
    Each day has a different post type optimized for community engagement:

    - **Monday:** Value-driven teaching posts
    - **Tuesday:** Offer posts showcasing paid community value
    - **Wednesday:** Personal stories and behind-the-scenes
    - **Thursday:** Cross-platform content sharing
    - **Friday:** Community wins and member spotlights
    - **Weekend:** Off-topic, personal connection posts

    **Parameters:**
    - **topic**: Title/headline of the post (required)
    - **content_details**: The full content, story, or details to work with (optional but recommended)
    - **day**: Override auto-detection to use specific day template (optional)
    - **inputs**: Day-specific inputs like member names, platforms, etc. (optional)
    - **additional_context**: Tone, style, or other requirements (optional)

    **Example 1 (Monday Value Post - with content_details):**
    ```json
    {
      "topic": "3 things every AI Agent should have",
      "content_details": "1) Error handling with exponential backoff - catches API failures and retries intelligently. 2) Structured logging using JSON format - makes debugging 10x easier. 3) State persistence with Redis - tracks progress across runs so you can resume.",
      "additional_context": "Make it beginner-friendly"
    }
    ```

    **Example 2 (Wednesday Personal Story):**
    ```json
    {
      "topic": "When I over-engineered my automation",
      "day": "wednesday",
      "content_details": "I spent 2 weeks building a custom state manager for my AI agents. Created a whole PostgreSQL system with tables for tracking which APIs were called. Then I read the CrewAI Flows docs more carefully and realized it handles state automatically. Total facepalm moment.",
      "additional_context": "Make it vulnerable and relatable"
    }
    ```

    **Example 3 (Friday Community Win):**
    ```json
    {
      "topic": "Community wins this week",
      "day": "friday",
      "content_details": "Sarah just connected Airtable to CrewAI to generate daily leads automatically. She went from manually entering 50 leads a day to having it all automated.",
      "inputs": {
        "member_name": "Sarah"
      }
    }
    ```

    **Example 4 (Simple - auto-detect day):**
    ```json
    {
      "topic": "Quick tip for debugging AI agents"
    }
    ```
    """
    try:
        # Generate Skool post
        result = skool_content_service.generate_post(
            topic=request.topic,
            day=request.day,
            content_details=request.content_details,
            inputs=request.inputs,
            additional_context=request.additional_context
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skool post generation failed: {str(e)}")
