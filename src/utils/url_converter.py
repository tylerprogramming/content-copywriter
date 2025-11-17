"""
URL Converter Utilities

Converts various file sharing URLs to direct download URLs.
"""

import re
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def convert_google_drive_url(url: str) -> str:
    """
    Convert Google Drive share URL to direct download URL

    Converts:
        https://drive.google.com/file/d/{FILE_ID}/view?usp=drive_link
    To:
        https://drive.google.com/uc?export=download&id={FILE_ID}

    Args:
        url: Google Drive share URL

    Returns:
        Direct download URL

    Example:
        >>> url = "https://drive.google.com/file/d/1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq/view?usp=drive_link"
        >>> convert_google_drive_url(url)
        'https://drive.google.com/uc?export=download&id=1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq'
    """
    # Pattern to extract file ID from Google Drive URL
    pattern = r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)'

    match = re.search(pattern, url)
    if not match:
        logger.warning(f"Could not extract file ID from Google Drive URL: {url}")
        return url

    file_id = match.group(1)
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    logger.info(f"Converted Google Drive URL: {file_id}")
    return direct_url


def is_google_drive_url(url: str) -> bool:
    """
    Check if URL is a Google Drive link

    Args:
        url: URL to check

    Returns:
        True if URL is from Google Drive
    """
    return 'drive.google.com' in url


def convert_url_for_upload(url: str) -> str:
    """
    Convert any supported sharing URL to direct download URL

    Currently supports:
    - Google Drive share links

    Args:
        url: File sharing URL

    Returns:
        Direct download URL (converted if needed, original if not)

    Example:
        >>> url = "https://drive.google.com/file/d/ABC123/view?usp=drive_link"
        >>> convert_url_for_upload(url)
        'https://drive.google.com/uc?export=download&id=ABC123'

        >>> url = "https://example.com/image.jpg"
        >>> convert_url_for_upload(url)
        'https://example.com/image.jpg'
    """
    # Google Drive URLs
    if is_google_drive_url(url):
        return convert_google_drive_url(url)

    # Add more converters here as needed
    # elif is_dropbox_url(url):
    #     return convert_dropbox_url(url)

    # Return original URL if no conversion needed
    logger.debug(f"No conversion needed for URL: {url[:50]}...")
    return url
