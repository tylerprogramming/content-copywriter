from typing import List, Optional
from datetime import datetime

from src.services.media_service import MediaService
from src.services.publishing_service import PublishingService
from src.blotato.models import MediaUploadResponse, MediaUploadWithRecordResponse, PostResponse
from src.blotato.exceptions import BlotatoAPIError, BlotatoValidationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentService:
    """
    Combined service for uploading media and publishing posts.
    Handles the complete workflow from Google Drive URL to published post.
    """
    
    def __init__(self, api_key: str = None):
        self.media_service = MediaService(api_key)
        self.publishing_service = PublishingService(api_key)
    
    def upload_and_publish(self, google_drive_url: str, account_id: str, 
                          platform: str, text: str, account_context: str = None,
                          scheduled_time: datetime = None) -> tuple[MediaUploadWithRecordResponse, PostResponse]:
        """
        Complete workflow: Upload media from Google Drive and publish as post
        
        Args:
            google_drive_url: Google Drive sharing URL for media
            account_id: Blotato account ID for the platform  
            platform: Target platform (tiktok, instagram, facebook, etc.)
            text: Post content text
            account_context: Context for logging (e.g., "tiktok", "instagram")
            scheduled_time: Optional scheduling time
            
        Returns:
            Tuple of (MediaUploadWithRecordResponse, PostResponse)
        """
        logger.info(f"Starting upload and publish workflow for {platform}")
        
        try:
            # Step 1: Upload media from Google Drive
            logger.info("Step 1: Uploading media from Google Drive...")
            
            media_with_record = self.media_service.upload_from_google_drive(
                google_drive_url, 
                account_context=account_context
            )
            
            logger.info(f"Media uploaded: {media_with_record.media_response.url}")
            
            # Step 2: Publishing post to social media with record ID
            logger.info("Step 2: Publishing post to social media...")
            post_response = self.publishing_service.publish_post(
                account_id=account_id,
                platform=platform,
                text=text,
                media_urls=[str(media_with_record.media_response.url)],
                scheduled_time=scheduled_time,
                account_context=account_context,
                media_upload_record_id=media_with_record.airtable_record_id
            )
            
            logger.info(f"Post published: {post_response.postSubmissionId}")
            logger.info("✅ Complete workflow finished successfully!")
            
            return media_with_record, post_response
            
        except Exception as e:
            logger.error(f"❌ Upload and publish workflow failed: {str(e)}")
            raise
    
    def upload_multiple_and_publish(self, google_drive_urls: List[str], 
                                   account_id: str, platform: str, text: str,
                                   account_context: str = None, 
                                   scheduled_time: datetime = None) -> tuple[List[MediaUploadResponse], PostResponse]:
        """
        Upload multiple media files and publish as single post
        
        Args:
            google_drive_urls: List of Google Drive sharing URLs
            account_id: Blotato account ID for the platform
            platform: Target platform
            text: Post content text
            account_context: Context for logging
            scheduled_time: Optional scheduling time
            
        Returns:
            Tuple of (List[MediaUploadResponse], PostResponse)
        """
        logger.info(f"Starting multi-media upload and publish workflow for {platform}")
        
        try:
            # Step 1: Upload all media files
            media_responses = []
            media_urls = []
            
            for i, url in enumerate(google_drive_urls, 1):
                logger.info(f"Uploading media {i}/{len(google_drive_urls)}...")
                media_response = self.media_service.upload_from_google_drive(
                    url, 
                    account_context=account_context
                )
                media_responses.append(media_response)
                media_urls.append(str(media_response.url))
                logger.info(f"Media {i} uploaded: {media_response.url}")
            
            # Step 2: Publish post with all uploaded media
            logger.info("Publishing post with all media...")
            post_response = self.publishing_service.publish_post(
                account_id=account_id,
                platform=platform,
                text=text,
                media_urls=media_urls,
                scheduled_time=scheduled_time,
                account_context=account_context
            )
            
            logger.info(f"Post published: {post_response.postSubmissionId}")
            logger.info("✅ Multi-media workflow finished successfully!")
            
            return media_responses, post_response
            
        except Exception as e:
            logger.error(f"❌ Multi-media workflow failed: {str(e)}")
            raise
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported social media platforms"""
        return self.publishing_service.get_supported_platforms()