from typing import List, Optional
from datetime import datetime
import time
import traceback

from src.blotato.client import BlotatoClient
from src.blotato.models import PostRequest, Post, PostContent, TikTokTarget, YouTubeTarget, GenericTarget, PlatformType, PostResponse
from src.blotato.exceptions import BlotatoAPIError, BlotatoValidationError
from src.services.airtable_service import AirtableService
from src.utils.logger import setup_logger
from src.config import config

logger = setup_logger(__name__)

class PublishingService:
    """Service for publishing posts to social media platforms via Blotato API"""
    
    def __init__(self, api_key: str = None):
        self.client = BlotatoClient(api_key)
        try:
            self.airtable = AirtableService()
        except Exception as e:
            logger.warning(f"Airtable service not available: {str(e)}")
            self.airtable = None
    
    def publish_post(self, account_id: str, platform: str, text: str, 
                    media_urls: List[str] = None, scheduled_time: datetime = None,
                    account_context: str = None, media_upload_record_id: str = None) -> PostResponse:
        """
        Publish a post to a social media platform with Airtable logging
        
        Args:
            account_id: Blotato account ID for the platform
            platform: Target platform (tiktok, instagram, facebook, etc.)
            text: Post content text
            media_urls: List of media URLs (from Blotato media upload)
            scheduled_time: Optional scheduling time
            account_context: Context for logging (e.g., "tiktok", "instagram")
            media_upload_record_id: ID of media upload record to update with publishing info
            
        Returns:
            PostResponse with submission ID
        """
        start_time = time.time()
        
        try:
            # Validate platform
            try:
                platform_enum = PlatformType(platform.lower())
            except ValueError:
                raise BlotatoValidationError(f"Unsupported platform: {platform}")
            
            # Create post request
            post_content = PostContent(
                text=text,
                mediaUrls=media_urls or [],
                platform=platform_enum
            )
            
            # Get platform-specific settings from config
            platform_settings = config.PLATFORM_SETTINGS.get(platform.lower(), {})
            
            # Build platform-specific target
            if platform_enum == PlatformType.TIKTOK:
                # Use settings from config with fallback defaults
                target_options = {
                    "privacyLevel": platform_settings.get("privacy_level", "PUBLIC_TO_EVERYONE"),
                    "disabledComments": platform_settings.get("disabled_comments", False),
                    "disabledDuet": platform_settings.get("disabled_duet", False), 
                    "disabledStitch": platform_settings.get("disabled_stitch", False),
                    "isBrandedContent": platform_settings.get("is_branded_content", False),
                    "isYourBrand": platform_settings.get("is_your_brand", False),
                    "isAiGenerated": platform_settings.get("is_ai_generated", False)
                }
                target = TikTokTarget(**target_options)
            elif platform_enum == PlatformType.YOUTUBE:
                # YouTube requires a title - use a default if not provided
                target_options = {
                    "title": "New Content",  # Default title
                    "privacyStatus": platform_settings.get("privacy_status", "public"),
                    "shouldNotifySubscribers": platform_settings.get("should_notify_subscribers", True),
                    "isMadeForKids": platform_settings.get("is_made_for_kids", False)
                }
                target = YouTubeTarget(**target_options)
            else:
                # Generic target for other platforms (Instagram, LinkedIn, etc.)
                target = GenericTarget(targetType=platform_enum)
            
            post_data = Post(
                accountId=account_id,
                content=post_content,
                target=target
            )
            
            post_request = PostRequest(
                post=post_data,
                scheduledTime=scheduled_time
            )
            
            # Publish via Blotato API
            response = self.client.publish_post(post_request)
            processing_duration = int(time.time() - start_time)
            
            logger.info(f"Post published successfully: {response.postSubmissionId}")
            
            # Log publication to video-publications table
            if self.airtable and media_upload_record_id:
                self.airtable.log_video_publication(
                    video_upload_record_id=media_upload_record_id,
                    platform=platform,
                    post_submission_id=response.postSubmissionId,
                    post_text=text,
                    publication_status="Success"
                )
                
                # Reduced logging - only log critical info
            
            return response
            
        except (BlotatoAPIError, BlotatoValidationError) as e:
            # Log error to system logs
            if self.airtable:
                error_code = type(e).__name__.replace("Blotato", "").replace("Error", "").upper()
                self.airtable.log_error(
                    component="PublishingService",
                    message=f"Post publishing failed: {str(e)}",
                    upload_id=media_upload_record_id,
                    error_code=error_code,
                    request_data={
                        "account_id": account_id,
                        "platform": platform,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "media_urls": media_urls or [],
                        "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
                        "account_context": account_context
                    }
                )
            
            logger.error(f"Post publishing failed: {str(e)}")
            raise
            
        except Exception as e:
            # Log unexpected error to system logs
            if self.airtable:
                self.airtable.log_error(
                    component="PublishingService",
                    message=f"Unexpected error during post publishing: {str(e)}",
                    upload_id=media_upload_record_id,
                    stack_trace=traceback.format_exc(),
                    request_data={
                        "account_id": account_id,
                        "platform": platform,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "media_urls": media_urls or [],
                        "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
                        "account_context": account_context
                    }
                )
            
            logger.error(f"Unexpected post publishing error: {str(e)}")
            raise BlotatoAPIError(f"Post publishing failed with unexpected error: {str(e)}")
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported social media platforms"""
        return [platform.value for platform in PlatformType]