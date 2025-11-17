from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Union, List
from enum import Enum
from datetime import datetime

class MediaUploadRequest(BaseModel):
    url: str

    @validator('url')
    def validate_url(cls, v):
        if v.startswith('data:'):
            return v
        try:
            HttpUrl(v)
            return v
        except:
            raise ValueError('url must be a valid URL or base64 data URI')

class MediaUploadFromUrlRequest(BaseModel):
    """Request to upload media from a URL (supports Google Drive links)"""
    url: str

    @validator('url')
    def validate_url(cls, v):
        # Basic URL validation - will be converted if Google Drive
        if not v.startswith(('http://', 'https://', 'data:')):
            raise ValueError('url must start with http://, https://, or data:')
        return v

class MediaUploadResponse(BaseModel):
    url: HttpUrl

class MediaUploadFromUrlResponse(BaseModel):
    """Response for URL-based media upload"""
    success: bool
    media_url: str
    original_url: str
    converted_url: Optional[str] = None
    message: str

class MediaUploadWithRecordResponse(BaseModel):
    """Extended response that includes Airtable record ID"""
    media_response: MediaUploadResponse
    airtable_record_id: Optional[str] = None

class BlotatoError(BaseModel):
    error: str
    message: Optional[str] = None
    status_code: Optional[int] = None

class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin" 
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    THREADS = "threads"
    BLUESKY = "bluesky"
    YOUTUBE = "youtube"

class PostContent(BaseModel):
    text: str
    mediaUrls: List[str] = []
    platform: PlatformType
    additionalPosts: Optional[List[dict]] = None

class TikTokTarget(BaseModel):
    """TikTok-specific target configuration"""
    targetType: PlatformType = PlatformType.TIKTOK
    privacyLevel: str = "SELF_ONLY"  # "PUBLIC", "FRIENDS", "SELF_ONLY" 
    disabledComments: bool = False
    disabledDuet: bool = False
    disabledStitch: bool = False
    isBrandedContent: bool = False
    isYourBrand: bool = False
    isAiGenerated: bool = False

class YouTubeTarget(BaseModel):
    """YouTube-specific target configuration"""
    targetType: PlatformType = PlatformType.YOUTUBE
    title: str  # Required for YouTube
    privacyStatus: str = "public"  # "private", "public", "unlisted"
    shouldNotifySubscribers: bool = True
    isMadeForKids: bool = False

class GenericTarget(BaseModel):
    """Generic target for platforms without specific settings"""
    targetType: PlatformType

class PostTarget(BaseModel):
    """Generic post target - use specific target classes instead"""
    pass

class Post(BaseModel):
    accountId: str
    content: PostContent
    target: Union[TikTokTarget, YouTubeTarget, GenericTarget]

class PostRequest(BaseModel):
    post: Post
    scheduledTime: Optional[datetime] = None

class PostResponse(BaseModel):
    postSubmissionId: str