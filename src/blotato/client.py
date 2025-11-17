import requests
import time
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from src.config import config
from src.utils.logger import setup_logger
from .models import MediaUploadRequest, MediaUploadResponse, BlotatoError, PostRequest, PostResponse
from .exceptions import BlotatoAPIError, BlotatoRateLimitError, BlotatoAuthenticationError

logger = setup_logger(__name__)

class BlotatoClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.API_KEY
        self.base_url = base_url or config.API_BASE_URL
        self.session = requests.Session()
        
        if not self.api_key:
            raise BlotatoAuthenticationError("API key is required")
        
        self.session.headers.update({
            "blotato-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        
        self._last_request_time = 0
        self._request_count = 0
        self._minute_start = time.time()
    
    def _rate_limit_check(self):
        current_time = time.time()
        
        if current_time - self._minute_start >= 60:
            self._request_count = 0
            self._minute_start = current_time
        
        if self._request_count >= config.MAX_REQUESTS_PER_MINUTE:
            sleep_time = 60 - (current_time - self._minute_start)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self._request_count = 0
                self._minute_start = time.time()
        
        self._request_count += 1
        self._last_request_time = current_time
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        self._rate_limit_check()
        
        # Fix urljoin issue - ensure base_url ends with / for proper joining
        base = self.base_url.rstrip('/') + '/'
        endpoint = endpoint.lstrip('/')
        url = urljoin(base, endpoint)
        logger.debug(f"Making {method} request to: {url}")
        
        try:
            # Increase timeout for large file uploads
            if 'json' in kwargs and 'url' in kwargs.get('json', {}):
                if kwargs['json']['url'].startswith('data:'):
                    kwargs['timeout'] = 300  # 5 minutes for base64 uploads
                    # Configure session for large uploads
                    self.session.mount('https://', requests.adapters.HTTPAdapter(
                        max_retries=requests.packages.urllib3.util.retry.Retry(
                            total=3,
                            backoff_factor=1,
                            status_forcelist=[502, 503, 504]
                        )
                    ))
            
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 429:
                raise BlotatoRateLimitError("Rate limit exceeded", status_code=429)
            elif response.status_code == 401:
                raise BlotatoAuthenticationError("Invalid API key", status_code=401)
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise BlotatoAPIError(
                        error_data.get("message", f"API error: {response.status_code}"),
                        status_code=response.status_code
                    )
                except ValueError:
                    raise BlotatoAPIError(
                        f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise BlotatoAPIError(f"Request failed: {str(e)}")
    
    def upload_media(self, url: str) -> MediaUploadResponse:
        request_data = MediaUploadRequest(url=url)
        
        logger.info(f"Uploading media from URL: {url[:100]}...")
        
        response_data = self._make_request(
            "POST",
            "/media",
            json=request_data.dict()
        )
        
        response = MediaUploadResponse(**response_data)
        logger.info(f"Media uploaded successfully: {response.url}")
        
        return response
    
    def publish_post(self, post_request: PostRequest) -> PostResponse:
        """
        Publish a post to social media platform
        
        Args:
            post_request: PostRequest containing post data and scheduling info
            
        Returns:
            PostResponse with submission ID
        """
        logger.info(f"Publishing post to {post_request.post.content.platform}")
        
        # Convert datetime to ISO string if scheduled
        request_data = post_request.dict(exclude_none=True)
        if post_request.scheduledTime:
            request_data["scheduledTime"] = post_request.scheduledTime.isoformat()
        
        response_data = self._make_request(
            "POST", 
            "/posts",
            json=request_data
        )
        
        response = PostResponse(**response_data)
        logger.info(f"Post submitted successfully: {response.postSubmissionId}")

        return response

    def generate_carousel(self, inputs: Dict, template_id: str, render: bool = True, is_draft: bool = False) -> Dict:
        """
        Generate a carousel post using Blotato templates

        Args:
            inputs: Template inputs (theme, quotes, profile info, etc.)
            template_id: Blotato template ID
            render: Whether to render immediately (default: True)
            is_draft: Save as draft instead of publishing (default: False)

        Returns:
            Dict with Blotato API response

        Example:
            inputs = {
                "theme": "light",
                "handle": "tylerreedai",
                "quotes": ["Quote 1", "Quote 2"],
                "verified": True,
                "authorName": "Tyler Reed",
                "aspectRatio": "4:5",
                "profileImage": "https://example.com/profile.jpg"
            }
            response = client.generate_carousel(
                inputs=inputs,
                template_id="/base/v2/tweet-card/.../v1"
            )
        """
        logger.info(f"Generating carousel with template: {template_id}")
        logger.info(f"Carousel inputs: {len(inputs.get('quotes', []))} slides")

        request_payload = {
            "inputs": inputs,
            "render": render,
            "isDraft": is_draft,
            "templateId": template_id
        }

        response_data = self._make_request(
            "POST",
            "/videos/from-templates",
            json=request_payload
        )

        logger.info(f"Carousel generated successfully")

        return response_data

    def list_templates(self, fields: Optional[str] = None, search: Optional[str] = None, template_id: Optional[str] = None) -> Dict:
        """
        List all available Blotato templates

        Args:
            fields: Comma-separated list of fields to include (default: id,title,description)
                    Example: "id,title,description,inputs"
            search: Search regex term to filter templates by title or description
                    Example: "tweet" or "real estate"
            template_id: If provided, only return the template with this ID
                        Example: "/base/v2/tweet-card/9714ae5c-7e6b-4878-be4a-4b1ba5d0cd66/v1"

        Returns:
            Dict with list of templates in "items" key

        Example:
            # List all templates (basic info)
            templates = client.list_templates()

            # List with full details including input parameters
            templates = client.list_templates(fields="id,title,description,inputs")

            # Search for tweet-related templates
            templates = client.list_templates(search="tweet")

            # Get specific template
            template = client.list_templates(template_id="/base/v2/tweet-card/.../v1")
        """
        logger.info("Fetching available Blotato templates")

        # Build query parameters
        params = {}
        if fields:
            params["fields"] = fields
        if search:
            params["search"] = search
        if template_id:
            params["id"] = template_id

        response_data = self._make_request(
            "GET",
            "/videos/templates",
            params=params
        )

        template_count = len(response_data.get("items", []))
        logger.info(f"Retrieved {template_count} template(s)")

        return response_data

    def get_video(self, video_id: str) -> Dict:
        """
        Get a single video by its ID

        Retrieves the video by its ID. This is useful for polling after creating
        a video programmatically to check its status and get the final URL.

        Args:
            video_id: The video ID
                     Example: "123e4567-e89b-12d3-a456-426614174000"

        Returns:
            Dict with video details including id, status, createdAt, mediaUrl

        Example:
            video = client.get_video("123e4567-e89b-12d3-a456-426614174000")
            if video["status"] == "completed":
                print(f"Video ready: {video['mediaUrl']}")
        """
        logger.info(f"Fetching video: {video_id}")

        response_data = self._make_request(
            "GET",
            f"/videos/creations/{video_id}"
        )

        logger.info(f"Retrieved video {video_id}, status: {response_data.get('item', {}).get('status')}")

        return response_data