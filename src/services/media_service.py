from typing import Dict, Any, Optional
from urllib.parse import urlparse
import time
import traceback

from src.blotato.client import BlotatoClient
from src.blotato.exceptions import BlotatoAPIError, BlotatoValidationError
from src.blotato.models import MediaUploadResponse, MediaUploadWithRecordResponse
from src.utils.google_drive import GoogleDriveService
from src.utils.logger import setup_logger
from src.services.airtable_service import AirtableService

logger = setup_logger(__name__)

class MediaService:
    """Service for handling media uploads via Blotato API"""
    
    def __init__(self, api_key: str = None):
        self.client = BlotatoClient(api_key)
        self.google_drive = GoogleDriveService()
        try:
            self.airtable = AirtableService()
        except Exception as e:
            logger.warning(f"Airtable service not available: {str(e)}")
            self.airtable = None
    
    def upload_from_url(self, url: str, social_account: str = None) -> MediaUploadWithRecordResponse:
        """
        Upload media from any supported URL with Airtable logging.
        Automatically handles Google Drive URL conversion.
        
        Args:
            url: URL to upload from (Google Drive sharing link or direct URL)
            social_account: Which account this is for (e.g., "tiktok", "instagram")
            
        Returns:
            MediaUploadWithRecordResponse with uploaded media URL and Airtable record ID
            
        Raises:
            BlotatoValidationError: If URL is invalid
            BlotatoAPIError: If upload fails
        """
        start_time = time.time()
        upload_record_id = None
        
        try:
            if not url or not url.strip():
                raise BlotatoValidationError("URL cannot be empty")
            
            url = url.strip()
            
            # Validate URL format
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    raise BlotatoValidationError("Invalid URL format")
            except Exception:
                raise BlotatoValidationError("Invalid URL format")
            
            # Convert Google Drive URLs to direct download links
            processed_url = url
            file_id = None
            
            if self.google_drive.is_google_drive_url(url):
                if not self.google_drive.validate_google_drive_url(url):
                    raise BlotatoValidationError("Invalid Google Drive URL - cannot extract file ID")
                
                file_id = self.google_drive.extract_file_id(url)
                processed_url = self.google_drive.convert_to_direct_url(url)
                logger.info(f"Converted Google Drive URL for upload")
            
            # Log upload start to Airtable
            if self.airtable and file_id:
                upload_record_id = self.airtable.log_upload_start(
                    google_drive_url=url,
                    file_id=file_id,
                    converted_url=processed_url,
                    social_account=social_account
                )
            
            # Upload via Blotato API
            response = self.client.upload_media(processed_url)
            processing_duration = int(time.time() - start_time)
            
            logger.info(f"Media uploaded successfully: {response.url}")
            
            # Log success to Airtable with request/response data
            if self.airtable and upload_record_id:
                self.airtable.log_upload_success(
                    record_id=upload_record_id,
                    blotato_url=str(response.url)
                )
                
                # Log detailed request/response data
                self.airtable.log_info(
                    component="MediaService",
                    message=f"Upload completed successfully: {response.url}",
                    upload_id=upload_record_id,
                    request_data={
                        "original_url": url,
                        "converted_url": processed_url,
                        "social_account": social_account,
                        "file_id": file_id
                    },
                    response_data={
                        "blotato_url": str(response.url),
                        "processing_duration": processing_duration,
                        "upload_status": "Success"
                    }
                )
            
            return MediaUploadWithRecordResponse(
                media_response=response,
                airtable_record_id=upload_record_id
            )
            
        except (BlotatoAPIError, BlotatoValidationError) as e:
            # Log failure to Airtable
            if self.airtable and upload_record_id:
                error_code = type(e).__name__.replace("Blotato", "").replace("Error", "").upper()
                self.airtable.log_upload_failure(
                    record_id=upload_record_id,
                    error_message=str(e),
                    error_code=error_code
                )
                
                # Log detailed error with request data
                self.airtable.log_error(
                    component="MediaService",
                    message=f"Upload failed: {str(e)}",
                    upload_id=upload_record_id,
                    error_code=error_code,
                    request_data={
                        "original_url": url,
                        "converted_url": processed_url if 'processed_url' in locals() else url,
                        "social_account": social_account,
                        "file_id": file_id if 'file_id' in locals() else None
                    }
                )
            
            logger.error(f"Upload failed: {str(e)}")
            raise
            
        except Exception as e:
            # Log unexpected error to Airtable
            if self.airtable and upload_record_id:
                self.airtable.log_upload_failure(
                    record_id=upload_record_id,
                    error_message=str(e),
                    error_code="UNEXPECTED_ERROR"
                )
            
            # Also log to Airtable system logs
            if self.airtable:
                self.airtable.log_error(
                    component="MediaService",
                    message=f"Unexpected error during upload: {str(e)}",
                    upload_id=upload_record_id,
                    stack_trace=traceback.format_exc(),
                    request_data={
                        "original_url": url,
                        "converted_url": processed_url if 'processed_url' in locals() else url,
                        "social_account": social_account,
                        "file_id": file_id if 'file_id' in locals() else None
                    }
                )
            
            logger.error(f"Unexpected upload error: {str(e)}")
            raise BlotatoAPIError(f"Upload failed with unexpected error: {str(e)}")
    
    def upload_from_google_drive(self, sharing_url: str, social_account: str = None) -> MediaUploadWithRecordResponse:
        """
        Upload media specifically from Google Drive sharing URL.
        
        Args:
            sharing_url: Google Drive sharing URL
            social_account: Which account this is for
            
        Returns:
            MediaUploadWithRecordResponse with uploaded media URL and Airtable record ID
        """
        if not self.google_drive.is_google_drive_url(sharing_url):
            raise BlotatoValidationError("URL is not a Google Drive URL")
        
        return self.upload_from_url(sharing_url, social_account)
    
    def get_upload_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a URL before uploading.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with URL analysis information
        """
        info = {
            "original_url": url,
            "is_google_drive": False,
            "converted_url": url,
            "file_id": None,
            "valid": False
        }
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return info
            
            if self.google_drive.is_google_drive_url(url):
                info["is_google_drive"] = True
                info["file_id"] = self.google_drive.extract_file_id(url)
                info["converted_url"] = self.google_drive.convert_to_direct_url(url)
                info["valid"] = self.google_drive.validate_google_drive_url(url)
            else:
                info["valid"] = True
            
        except Exception as e:
            logger.error(f"Error analyzing URL: {str(e)}")
        
        return info