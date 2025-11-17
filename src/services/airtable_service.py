import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.config import config
from src.utils.logger import setup_logger

try:
    from pyairtable import Api
    AIRTABLE_AVAILABLE = True
except ImportError:
    Api = None
    AIRTABLE_AVAILABLE = False

logger = setup_logger(__name__)

class MediaUploadRecord(BaseModel):
    """Data model for clean media upload records"""
    google_drive_url: str
    google_drive_file_id: str
    converted_url: str
    blotato_media_url: Optional[str] = None
    upload_status: str = "Processing"
    upload_time: Optional[datetime] = None
    error_message: Optional[str] = None
    social_account: Optional[str] = None  # Changed from account_context

class VideoPublicationRecord(BaseModel):
    """Data model for individual video publication records"""
    video_upload_record: str  # Link to video-uploads table (Airtable record ID)
    platform: str  # tiktok, linkedin, etc.
    post_submission_id: str  # From Blotato
    post_text: str
    publication_status: str = "Success"  # Success, Failed, Pending, Scheduled
    scheduled_date: Optional[datetime] = None  # When post is scheduled for
    error_message: Optional[str] = None


class SystemLogRecord(BaseModel):
    """Data model for system log records"""
    upload_id: Optional[str] = None  # Link to media upload record
    log_level: str = "INFO"
    component: str
    message: str
    session_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    user_agent: str = "Blotato-Service-v1.0.0"

class AirtableService:
    """Service for logging data to Airtable"""
    
    def __init__(self):
        if not AIRTABLE_AVAILABLE:
            raise ValueError("pyairtable package not installed. Run: pip install pyairtable")
        
        if not config.AIRTABLE_API_KEY or not config.AIRTABLE_BASE_ID:
            raise ValueError("Airtable credentials not configured")
        
        self.api = Api(config.AIRTABLE_API_KEY)
        self.base_id = config.AIRTABLE_BASE_ID
        
        # Table names from config
        self.media_uploads_table = config.TABLE_NAMES["media_uploads"]
        self.video_publications_table = config.TABLE_NAMES["video_publications"]
        self.system_logs_table = config.TABLE_NAMES["system_logs"]
        
        self.session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"AirtableService initialized with session: {self.session_id}")
    
    def create_media_upload_record(self, record: MediaUploadRecord) -> str:
        """
        Create a new media upload record in Airtable
        
        Args:
            record: MediaUploadRecord data
            
        Returns:
            Airtable record ID
        """
        try:
            table = self.api.table(self.base_id, self.media_uploads_table)
            
            # Prepare fields for Airtable
            fields = {
                "Google Drive URL": record.google_drive_url,
                "Google Drive File ID": record.google_drive_file_id,
                "Converted URL": record.converted_url,
                "Upload Status": record.upload_status,
                "Created At": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add optional fields if present
            if record.blotato_media_url:
                fields["Blotato Media URL"] = record.blotato_media_url
            
            if record.upload_time:
                fields["Upload Time"] = record.upload_time.strftime("%Y-%m-%d")
            
            if record.error_message:
                fields["Error Message"] = record.error_message
            
            # Social Account is now a computed field (lookup from publications), don't write to it
            # if record.social_account:
            #     fields["Social Account"] = record.social_account
            
            # Campaign and Tags fields removed from database
            # if record.campaign:
            #     fields["Campaign"] = record.campaign
            # 
            # if record.tags:
            #     fields["Tags"] = record.tags
            
            # Create record
            created_record = table.create(fields)
            record_id = created_record["id"]
            
            logger.info(f"Created media upload record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create media upload record: {str(e)}")
            raise
    
    def create_video_publication_record(self, record: VideoPublicationRecord) -> str:
        """
        Create a new video publication record in Airtable
        
        Args:
            record: VideoPublicationRecord data
            
        Returns:
            Airtable record ID
        """
        try:
            table = self.api.table(self.base_id, self.video_publications_table)
            
            # Prepare fields for Airtable
            fields = {
                "Video Upload Record": [record.video_upload_record],  # Link field
                "Platform": record.platform,
                "Post Submission ID": record.post_submission_id,
                "Post Text": record.post_text,
                "Publication Status": record.publication_status
            }
            
            # Add optional fields if present
            if record.scheduled_date:
                fields["Scheduled Date"] = record.scheduled_date.strftime("%Y-%m-%d %H:%M:%S")
            if record.error_message:
                fields["Error Message"] = record.error_message
            
            # Create record
            created_record = table.create(fields)
            record_id = created_record["id"]
            
            logger.info(f"Created video publication record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create media upload record: {str(e)}")
            raise
    
    def update_media_upload_record(self, record_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing media upload record
        
        Args:
            record_id: Airtable record ID
            updates: Fields to update
        """
        try:
            table = self.api.table(self.base_id, self.media_uploads_table)
            table.update(record_id, updates)
            
            logger.info(f"Updated media upload record: {record_id}")
            
        except Exception as e:
            logger.error(f"Failed to update media upload record {record_id}: {str(e)}")
            raise
    
    def create_system_log(self, record: SystemLogRecord) -> str:
        """
        Create a system log entry in Airtable
        
        Args:
            record: SystemLogRecord data
            
        Returns:
            Airtable record ID
        """
        try:
            # Note: Check that Timestamp field in media-logging table is set to "Date and time" type
            table = self.api.table(self.base_id, self.system_logs_table)
            
            # Prepare fields for Airtable
            fields = {
                "Log Level": record.log_level,
                "Component": record.component,
                "Message": record.message,
                "Timestamp": datetime.now().strftime("%m/%d/%Y %H:%M"),
                "Session ID": record.session_id or self.session_id,
                "User Agent": record.user_agent
            }
            
            # Add optional fields
            # Log ID is a computed field, so we can't write to it
            # Store upload_id in a different field or use it for reference only
            # if record.upload_id:
            #     fields["Log ID"] = [record.upload_id]
            
            if record.request_data:
                fields["Request Data"] = json.dumps(record.request_data, indent=2)
            
            if record.response_data:
                fields["Response Data"] = json.dumps(record.response_data, indent=2)
            
            if record.error_code:
                fields["Error Code"] = record.error_code
            
            if record.stack_trace:
                fields["Stack Trace"] = record.stack_trace
            
            # Create record
            created_record = table.create(fields)
            record_id = created_record["id"]
            
            logger.debug(f"Created system log: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create system log: {str(e)}")
            # Don't raise here to avoid logging loops
            return ""
    
    def add_tags_safely(self, record_id: str, tags: List[str]) -> None:
        """
        Add tags to a record, handling cases where new options aren't allowed
        """
        if not tags:
            return
        
        # Use configurable approved tags from config
        approved_tags = config.ALLOWED_TAGS
        
        # Filter to only include approved tags or try with all tags
        safe_tags = [tag for tag in tags if tag in approved_tags]
        
        try:
            # First try with only approved tags
            if safe_tags:
                self.update_media_upload_record(record_id, {"Tags": safe_tags})
                logger.info(f"Added approved tags: {safe_tags}")
            else:
                # Try with all tags - might work if field allows new options
                self.update_media_upload_record(record_id, {"Tags": tags})
                logger.info(f"Added all tags: {tags}")
                
        except Exception as e:
            if "INVALID_MULTIPLE_CHOICE_OPTIONS" in str(e):
                logger.warning(f"Cannot add tags {tags} - field restricted to predefined options")
                logger.info("To fix: In Airtable, go to Tags field settings and enable 'Allow users to add new options'")
            else:
                logger.error(f"Failed to add tags: {str(e)}")

    def log_upload_start(self, google_drive_url: str, file_id: str, converted_url: str, 
                        social_account: str = None) -> str:
        """
        Log the start of an upload process
        
        Returns:
            Media upload record ID
        """
        record = MediaUploadRecord(
            google_drive_url=google_drive_url,
            google_drive_file_id=file_id,
            converted_url=converted_url,
            upload_status="Processing",
            social_account=social_account
        )
        
        return self.create_media_upload_record(record)
    
    def log_upload_success(self, record_id: str, blotato_url: str) -> None:
        """
        Log successful upload completion
        """
        updates = {
            "Upload Status": "Success",
            "Blotato Media URL": blotato_url,
            "Upload Time": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.update_media_upload_record(record_id, updates)
        
        # Log system message
        self.log_info("MediaService", f"Upload completed successfully: {blotato_url}", 
                     upload_id=record_id)
    
    def log_upload_failure(self, record_id: str, error_message: str, 
                          error_code: str = None) -> None:
        """
        Log failed upload
        """
        updates = {
            "Upload Status": "Failed",
            "Error Message": error_message,
            "Upload Time": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.update_media_upload_record(record_id, updates)
        
        # Log system error (temporarily disabled - will be called from MediaService with full context)
        # self.log_error("MediaService", f"Upload failed: {error_message}", 
        #               upload_id=record_id, error_code=error_code)
    
    def log_info(self, component: str, message: str, upload_id: str = None, 
                request_data: Dict = None, response_data: Dict = None) -> None:
        """Log info level message"""
        record = SystemLogRecord(
            upload_id=upload_id,
            log_level="INFO",
            component=component,
            message=message,
            session_id=self.session_id,
            request_data=request_data,
            response_data=response_data
        )
        self.create_system_log(record)
    
    def log_error(self, component: str, message: str, upload_id: str = None,
                 error_code: str = None, stack_trace: str = None,
                 request_data: Dict = None) -> None:
        """Log error level message"""
        record = SystemLogRecord(
            upload_id=upload_id,
            log_level="ERROR",
            component=component,
            message=message,
            session_id=self.session_id,
            error_code=error_code,
            stack_trace=stack_trace,
            request_data=request_data
        )
        self.create_system_log(record)
    
    def log_warning(self, component: str, message: str, upload_id: str = None) -> None:
        """Log warning level message"""
        record = SystemLogRecord(
            upload_id=upload_id,
            log_level="WARNING",
            component=component,
            message=message,
            session_id=self.session_id
        )
        self.create_system_log(record)
    
    def log_video_publication(self, video_upload_record_id: str, platform: str, 
                             post_submission_id: str, post_text: str, 
                             publication_status: str = "Success", error_message: str = None) -> str:
        """
        Log a video publication event to the video-publications table
        
        Args:
            video_upload_record_id: ID of the video upload record
            platform: Target platform (tiktok, linkedin, etc.)
            post_submission_id: Post submission ID from Blotato
            post_text: The text content of the post
            publication_status: Success, Failed, or Pending
            error_message: Error message if publication failed
            
        Returns:
            Airtable publication record ID
        """
        try:
            record = VideoPublicationRecord(
                video_upload_record=video_upload_record_id,
                platform=platform,
                post_submission_id=post_submission_id,
                post_text=post_text,
                publication_status=publication_status,
                error_message=error_message
            )
            
            publication_record_id = self.create_video_publication_record(record)
            logger.info(f"Logged publication: {platform} -> {post_submission_id}")
            
            return publication_record_id
            
        except Exception as e:
            logger.error(f"Failed to log video publication: {str(e)}")
            raise
    
    def find_latest_unpublished_video(self) -> dict:
        """
        Find the most recent video upload that hasn't been published to any platform yet
        
        Returns:
            Dictionary with record info or None if no unpublished videos found
        """
        try:
            uploads_table = self.api.table(self.base_id, self.media_uploads_table)
            publications_table = self.api.table(self.base_id, self.video_publications_table)
            
            # Get all successful uploads sorted by created date (newest first)
            upload_records = uploads_table.all(
                sort=["-Created At"],
                formula="{Upload Status} = 'Success'"
            )
            
            if not upload_records:
                logger.info("No successful uploads found")
                return None
            
            # Get all publication records to check what's been published
            publication_records = publications_table.all()
            published_upload_ids = set()
            
            for pub_record in publication_records:
                # Extract upload record ID from linked field
                linked_records = pub_record["fields"].get("Video Upload Record", [])
                for upload_id in linked_records:
                    published_upload_ids.add(upload_id)
            
            # Find the first upload that hasn't been published
            for upload_record in upload_records:
                if upload_record["id"] not in published_upload_ids:
                    record_info = {
                        "record_id": upload_record["id"],
                        "google_drive_url": upload_record["fields"].get("Google Drive URL"),
                        "blotato_media_url": upload_record["fields"].get("Blotato Media URL"), 
                        "created_at": upload_record["fields"].get("Created At"),
                        "social_account": upload_record["fields"].get("Social Account"),
                        "upload_status": upload_record["fields"].get("Upload Status")
                    }
                    
                    logger.info(f"Found latest unpublished video: {record_info['record_id']}")
                    logger.info(f"Created: {record_info['created_at']}, Social Account: {record_info['social_account']}")
                    
                    return record_info
            
            logger.info("No unpublished videos found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to find latest unpublished video: {str(e)}")
            raise
    
    def find_videos_by_status(self, published: bool = False, limit: int = 10) -> list:
        """
        Find videos by publication status using the two-table approach
        
        Args:
            published: True to find published videos, False for unpublished
            limit: Maximum number of records to return
            
        Returns:
            List of video records
        """
        try:
            uploads_table = self.api.table(self.base_id, self.media_uploads_table)
            publications_table = self.api.table(self.base_id, self.video_publications_table)
            
            # Get all successful uploads
            upload_records = uploads_table.all(
                sort=["-Created At"],
                formula="{Upload Status} = 'Success'",
                max_records=limit * 2  # Get more to account for filtering
            )
            
            if not upload_records:
                return []
            
            # Get all publication records
            publication_records = publications_table.all()
            
            # Build set of published upload IDs and their platforms
            published_info = {}  # upload_id -> list of platforms
            for pub_record in publication_records:
                linked_records = pub_record["fields"].get("Video Upload Record", [])
                platform = pub_record["fields"].get("Platform", "")
                for upload_id in linked_records:
                    if upload_id not in published_info:
                        published_info[upload_id] = []
                    published_info[upload_id].append(platform)
            
            # Filter uploads based on publication status
            video_list = []
            for record in upload_records[:limit]:
                upload_id = record["id"]
                is_published = upload_id in published_info
                
                if published == is_published:
                    platforms = published_info.get(upload_id, [])
                    video_info = {
                        "record_id": upload_id,
                        "google_drive_url": record["fields"].get("Google Drive URL"),
                        "blotato_media_url": record["fields"].get("Blotato Media URL"),
                        "created_at": record["fields"].get("Created At"),
                        "social_account": record["fields"].get("Social Account"),
                        "published_platforms": platforms
                    }
                    video_list.append(video_info)
                    
                    if len(video_list) >= limit:
                        break
            
            status_text = "published" if published else "unpublished"
            logger.info(f"Found {len(video_list)} {status_text} videos")
            
            return video_list
            
        except Exception as e:
            logger.error(f"Failed to find videos by status: {str(e)}")
            raise
    
    def check_platform_published(self, upload_record_id: str, platform: str) -> bool:
        """
        Check if a specific platform has already been published for this upload record
        
        Args:
            upload_record_id: Video upload record ID
            platform: Platform name to check (tiktok, linkedin, etc.)
            
        Returns:
            True if already published to this platform, False otherwise
        """
        try:
            publications_table = self.api.table(self.base_id, self.video_publications_table)
            
            # Look for publication records that match this upload and platform
            records = publications_table.all(
                formula=f"AND(FIND('{upload_record_id}', {{Video Upload Record}}), {{Platform}} = '{platform}')"
            )
            
            is_published = len(records) > 0
            logger.info(f"Platform check for {platform}: {'Already published' if is_published else 'Not published yet'}")
            
            return is_published
            
        except Exception as e:
            logger.error(f"Failed to check platform published status: {str(e)}")
            # If we can't check, assume not published to be safe
            return False
    
    def find_latest_unpublished_for_platform(self, platform: str) -> dict:
        """
        Find the most recent video that hasn't been published to a specific platform yet
        
        Args:
            platform: Platform name (tiktok, linkedin, etc.)
            
        Returns:
            Dictionary with record info or None if no unpublished videos for this platform
        """
        try:
            uploads_table = self.api.table(self.base_id, self.media_uploads_table)
            publications_table = self.api.table(self.base_id, self.video_publications_table)
            
            # Get all successful uploads sorted by date
            upload_records = uploads_table.all(
                sort=["-Created At"],
                formula="{Upload Status} = 'Success'"
            )
            
            if not upload_records:
                logger.info("No successful uploads found")
                return None
            
            # Get all publication records for this platform
            platform_publications = publications_table.all(
                formula=f"{{Platform}} = '{platform}'"
            )
            
            # Build set of upload IDs already published to this platform
            published_upload_ids = set()
            for pub_record in platform_publications:
                linked_records = pub_record["fields"].get("Video Upload Record", [])
                for upload_id in linked_records:
                    published_upload_ids.add(upload_id)
            
            # Find the first upload not published to this platform
            for upload_record in upload_records:
                upload_id = upload_record["id"]
                
                if upload_id not in published_upload_ids:
                    # Found a record not published to this platform
                    record_info = {
                        "record_id": upload_id,
                        "google_drive_url": upload_record["fields"].get("Google Drive URL"),
                        "blotato_media_url": upload_record["fields"].get("Blotato Media URL"), 
                        "created_at": upload_record["fields"].get("Created At"),
                        "social_account": upload_record["fields"].get("Social Account"),
                        "upload_status": upload_record["fields"].get("Upload Status")
                    }
                    
                    logger.info(f"Found video not yet published to platform {platform}: {upload_id}")
                    logger.info(f"Created: {record_info['created_at']}, Social Account: {record_info['social_account']}")
                    
                    return record_info
            
            logger.info(f"No unpublished videos found for platform {platform}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to find latest unpublished video for platform: {str(e)}")
            raise