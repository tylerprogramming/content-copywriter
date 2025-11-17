"""
Platform-specific prompts for content generation

Loads prompts from text files in the prompts/ directory
"""

import os
from typing import Dict

# Path to prompts directory (at root level)
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts')


def _load_prompt_from_file(filename: str) -> str:
    """
    Load a prompt from a text file

    Args:
        filename: Name of the prompt file (e.g., 'linkedin.txt')

    Returns:
        Prompt text content

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    file_path = os.path.join(PROMPTS_DIR, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def _load_all_prompts() -> Dict[str, str]:
    """
    Load all prompt files from the prompts directory

    Returns:
        Dictionary mapping platform names to prompt content
    """
    prompts = {}

    # Standard prompts (text-only)
    prompt_files = {
        "youtube": "youtube_shorts.txt",
        "youtube_shorts": "youtube_shorts.txt",
        "linkedin": "linkedin_text.txt",
        "instagram": "instagram.txt",
        "tiktok": "tiktok.txt",
    }

    for platform, filename in prompt_files.items():
        try:
            prompts[platform] = _load_prompt_from_file(filename)
        except FileNotFoundError as e:
            print(f"Warning: Could not load prompt for {platform}: {e}")

    # LinkedIn video-specific prompt
    try:
        prompts["linkedin_video"] = _load_prompt_from_file("linkedin_video.txt")
    except FileNotFoundError as e:
        print(f"Warning: Could not load linkedin_video prompt: {e}")
        # Fallback to text-based LinkedIn prompt
        prompts["linkedin_video"] = prompts.get("linkedin", "")

    return prompts


# Load all prompts at module import
PLATFORM_PROMPTS = _load_all_prompts()


def get_prompt(platform: str, has_video: bool = False) -> str:
    """
    Get the prompt for a specific platform

    Args:
        platform: Platform name (youtube, linkedin, instagram, tiktok)
        has_video: If True and platform is LinkedIn, use the video-specific prompt

    Returns:
        Platform-specific prompt string

    Raises:
        ValueError: If platform is not supported
    """
    platform = platform.lower()

    # Use video-specific LinkedIn prompt if video is provided
    if platform == "linkedin" and has_video:
        prompt_key = "linkedin_video"
    else:
        prompt_key = platform

    if prompt_key not in PLATFORM_PROMPTS:
        supported = ", ".join([k for k in PLATFORM_PROMPTS.keys() if not k.endswith("_video")])
        raise ValueError(
            f"Platform '{platform}' not supported for content generation. "
            f"Supported platforms: {supported}"
        )

    return PLATFORM_PROMPTS[prompt_key]


def get_supported_platforms() -> list[str]:
    """Get list of supported platforms (excluding internal variants like linkedin_video)"""
    return ["youtube", "youtube_shorts", "linkedin", "instagram", "tiktok"]


__all__ = [
    "PLATFORM_PROMPTS",
    "get_prompt",
    "get_supported_platforms"
]
