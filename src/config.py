import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class BlotatoConfig:
    # API Configuration (from .env)
    API_BASE_URL: str = os.getenv("BLOTATO_API_BASE_URL", "https://backend.blotato.com/v2")
    API_KEY: Optional[str] = os.getenv("BLOTATO_API_KEY")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Airtable Configuration (from .env)
    AIRTABLE_API_KEY: Optional[str] = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: Optional[str] = os.getenv("AIRTABLE_BASE_ID")
    AIRTABLE_BASE_URL: str = "https://api.airtable.com/v0"
    
    # Rate limiting and file size limits
    MAX_REQUESTS_PER_MINUTE: int = 10
    MAX_FILE_SIZE_MB: int = 200
    
    # Airtable table names (update if your table names are different)
    TABLE_NAMES: dict = {
        "media_uploads": "video-uploads",
        "video_publications": "video-publications",
        "system_logs": "media-logging"
    }
    
    # Allowed tags for Airtable (if field is restricted to predefined options)
    ALLOWED_TAGS: list = [
        "Tutorial",
        "Demo", 
        "Promo",
        "Behind_Scenes",
        "Product",
        "Education",
        "CrewAI",
        "Marketing",
        "Social_Media",
        "Content_Creation",
        "Business",
        "Technology",
        "AI",
        "Automation",
        "Training",
        "Launch",
        "Update",
        "News",
        "Tips",
        "How_To"
    ]
    
    # Supported social media platforms
    SUPPORTED_PLATFORMS: list = [
        "tiktok",
        "facebook",
        "instagram",
        "youtube",
        "linkedin",
        "twitter",
        "threads",
        "bluesky",
        "pinterest"
    ]
    
    # Platform-specific posting settings
    PLATFORM_SETTINGS: dict = {
        "tiktok": {
            "privacy_level": "PUBLIC_TO_EVERYONE",  # Options: SELF_ONLY, PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR
            "disabled_comments": False,
            "disabled_duet": False,
            "disabled_stitch": False,
            "is_branded_content": False,
            "is_your_brand": False,
            "is_ai_generated": False
        },
        "youtube": {
            "privacy_status": "public",  # Options: private, public, unlisted
            "should_notify_subscribers": True,
            "is_made_for_kids": False
        }
    }
    
    @property 
    def PLATFORM_ACCOUNT_IDS(self) -> dict:
        """Get platform account IDs from environment variables"""
        account_ids = {}
        
        # Load account IDs from environment variables
        if os.getenv("TIKTOK_ACCOUNT_ID"):
            account_ids["tiktok"] = os.getenv("TIKTOK_ACCOUNT_ID")
        if os.getenv("INSTAGRAM_ACCOUNT_ID"):
            account_ids["instagram"] = os.getenv("INSTAGRAM_ACCOUNT_ID")
        if os.getenv("FACEBOOK_ACCOUNT_ID"):
            account_ids["facebook"] = os.getenv("FACEBOOK_ACCOUNT_ID")
        if os.getenv("YOUTUBE_ACCOUNT_ID"):
            account_ids["youtube"] = os.getenv("YOUTUBE_ACCOUNT_ID")
        if os.getenv("LINKEDIN_ACCOUNT_ID"):
            account_ids["linkedin"] = os.getenv("LINKEDIN_ACCOUNT_ID")
        if os.getenv("TWITTER_ACCOUNT_ID"):
            account_ids["twitter"] = os.getenv("TWITTER_ACCOUNT_ID")
        if os.getenv("THREADS_ACCOUNT_ID"):
            account_ids["threads"] = os.getenv("THREADS_ACCOUNT_ID")
        if os.getenv("BLUESKY_ACCOUNT_ID"):
            account_ids["bluesky"] = os.getenv("BLUESKY_ACCOUNT_ID")
        if os.getenv("PINTEREST_ACCOUNT_ID"):
            account_ids["pinterest"] = os.getenv("PINTEREST_ACCOUNT_ID")

        return account_ids
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.API_KEY:
            raise ValueError("BLOTATO_API_KEY environment variable is required")
        if not cls.AIRTABLE_API_KEY:
            raise ValueError("AIRTABLE_API_KEY environment variable is required")
        if not cls.AIRTABLE_BASE_ID:
            raise ValueError("AIRTABLE_BASE_ID environment variable is required")

    @staticmethod
    def load_model_config() -> Dict[str, Any]:
        """
        Load AI model configurations from YAML file

        Returns:
            dict: Model configuration with 'defaults' and 'platforms' keys
        """
        config_dir = Path(__file__).parent.parent / "config"
        models_file = config_dir / "models.yaml"

        if not models_file.exists():
            raise FileNotFoundError(
                f"Model configuration file not found: {models_file}\n"
                f"Please create config/models.yaml with model settings."
            )

        with open(models_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def get_model_config(platform: str, has_video: bool = False) -> Dict[str, Any]:
        """
        Get AI model configuration for specific platform and content type

        Args:
            platform: Platform name (e.g., 'linkedin', 'instagram')
            has_video: Whether content includes video (for platforms with separate configs)

        Returns:
            dict: Model configuration with 'model', 'temperature', 'max_tokens' keys

        Example:
            >>> config.get_model_config('linkedin', has_video=True)
            {'model': 'gpt-4o', 'temperature': 0.7, 'max_tokens': 2000}
        """
        model_config = BlotatoConfig.load_model_config()
        platform = platform.lower()

        # Get platform-specific config or use defaults
        platform_config = model_config["platforms"].get(platform)

        if not platform_config:
            return model_config["defaults"]

        # Check if platform has separate text/video configurations
        if isinstance(platform_config, dict) and "text" in platform_config:
            # Platform has separate configs for text and video
            content_type = "video" if has_video else "text"
            config_data = platform_config.get(content_type, platform_config.get("text"))

            # Remove 'description' key if present (not needed for API calls)
            if "description" in config_data:
                config_data = {k: v for k, v in config_data.items() if k != "description"}

            return config_data

        # Platform has single config for all content types
        if "description" in platform_config:
            platform_config = {k: v for k, v in platform_config.items() if k != "description"}

        return platform_config

config = BlotatoConfig()