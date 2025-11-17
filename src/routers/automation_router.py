"""
Automation API endpoints

Handles video transcription automation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.video_transcription_service import VideoTranscriptionService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize router
router = APIRouter(
    prefix="/automation",
    tags=["Automation"]
)


class TranscriptionRequest(BaseModel):
    """Request model for video transcription"""
    youtube_url: str


@router.post("/transcribe-video")
async def transcribe_video(request: TranscriptionRequest):
    """
    Transcribe a YouTube video using Apify

    Extracts transcript and metadata from a YouTube video without
    any database storage. Returns the raw transcription data.

    **Parameters:**
    - **youtube_url**: YouTube URL of the video to transcribe

    **Example:**
    ```json
    {
      "youtube_url": "https://youtu.be/NhwKQ7GwGq8"
    }
    ```

    **Response:**
    ```json
    {
      "success": true,
      "video_id": "NhwKQ7GwGq8",
      "title": "Video Title",
      "transcript": "Full transcript text...",
      "channel_name": "Channel Name",
      "duration": "10:30",
      "view_count": 12345,
      "likes": 500
    }
    ```

    **Workflow:**
    1. Extracts transcript from YouTube using Apify
    2. Returns transcript and video metadata
    """
    try:
        logger.info(f"Transcribing video: {request.youtube_url}")

        # Initialize transcription service
        transcription_service = VideoTranscriptionService()

        # Extract transcript using Apify
        result = transcription_service.extract_youtube_transcript(request.youtube_url)

        if not result or not result.get("transcript"):
            raise ValueError(f"Failed to extract transcript from: {request.youtube_url}")

        return {
            "success": True,
            "video_id": result.get("video_id"),
            "title": result.get("title"),
            "transcript": result.get("transcript"),
            "channel_name": result.get("channel_name"),
            "duration": result.get("duration"),
            "view_count": result.get("view_count"),
            "likes": result.get("likes")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
