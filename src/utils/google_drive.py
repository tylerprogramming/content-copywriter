from urllib.parse import urlparse, parse_qs
from typing import Optional
import re

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GoogleDriveService:
    """Service for handling Google Drive URL operations"""
    
    @staticmethod
    def is_google_drive_url(url: str) -> bool:
        """Check if URL is a Google Drive URL"""
        parsed = urlparse(url)
        return 'drive.google.com' in parsed.netloc
    
    @staticmethod
    def extract_file_id(url: str) -> Optional[str]:
        """Extract file ID from Google Drive URL"""
        if '/file/d/' in url:
            return url.split('/file/d/')[1].split('/')[0]
        
        # Try regex pattern for other formats
        pattern = r'(?:id=|/d/|/edit\?id=)([a-zA-Z0-9_-]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    @staticmethod
    def convert_to_direct_url(url: str) -> str:
        """Convert Google Drive sharing URL to direct download URL"""
        if not GoogleDriveService.is_google_drive_url(url):
            return url
        
        file_id = GoogleDriveService.extract_file_id(url)
        if not file_id:
            logger.warning(f"Could not extract file ID from URL: {url}")
            return url
        
        direct_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        logger.info(f"Converted Google Drive URL: {file_id}")
        return direct_url
    
    @staticmethod
    def validate_google_drive_url(url: str) -> bool:
        """Validate that Google Drive URL can be processed"""
        if not GoogleDriveService.is_google_drive_url(url):
            return False
        
        file_id = GoogleDriveService.extract_file_id(url)
        return file_id is not None