"""
AI Content Generation Service

Simplified service for generating platform-specific social media content
using OpenAI directly (no CrewAI overhead for simple content generation).
"""

import os
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.prompts import get_prompt
from src.utils.logger import setup_logger
from src.config import config

load_dotenv()

logger = setup_logger(__name__)


class GeneratedContent(BaseModel):
    """Generated content response"""
    title: str = Field(description="Engaging title/headline for the post")
    text: str = Field(description="Main post content with appropriate hashtags and formatting")
    platform: str = Field(description="Platform this content was generated for")
    character_count: int = Field(description="Total character count of the post text")


class AIContentService:
    """Service for generating platform-specific social media content using AI"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Content Service

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.logger = logger

    def generate_content(
        self,
        platform: str,
        input_text: str,
        video_transcript: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> GeneratedContent:
        """
        Generate platform-specific content from input text

        Args:
            platform: Target platform (youtube, linkedin, instagram, tiktok)
            input_text: Input text/topic to generate content from
            video_transcript: Optional video transcript to use as enhanced context
            additional_context: Optional additional context or requirements

        Returns:
            GeneratedContent with title and text

        Raises:
            ValueError: If platform is not supported
            Exception: If AI generation fails
        """
        try:
            # Get platform-specific prompt (use video variant for LinkedIn if transcript provided)
            has_video = video_transcript is not None
            platform_prompt = get_prompt(platform, has_video=has_video)

            # Build user message
            user_message = self._build_user_message(
                input_text=input_text,
                video_transcript=video_transcript,
                additional_context=additional_context
            )

            # Get model configuration from YAML
            model_config = config.get_model_config(platform, has_video=has_video)
            model_name = model_config.get("model", "gpt-4o-mini")
            temperature = model_config.get("temperature", 0.7)

            if video_transcript:
                prompt_type = "video" if platform == "linkedin" else "standard"
                self.logger.info(
                    f"🚀 Generating {platform} content ({prompt_type} prompt) "
                    f"using {model_name} from input + video transcript ({len(video_transcript)} chars)"
                )
            else:
                self.logger.info(f"🚀 Generating {platform} content using {model_name} from input")

            # Build API call parameters
            api_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": platform_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": temperature
            }

            # Only include max_tokens if specified in config (some models like gpt-5 don't use it)
            if "max_tokens" in model_config:
                api_params["max_tokens"] = model_config["max_tokens"]

            # Call OpenAI with model config from YAML
            response = self.client.chat.completions.create(**api_params)

            # Extract generated content
            generated_text = response.choices[0].message.content.strip()

            # Parse title and text
            title, text = self._parse_generated_content(generated_text)

            content = GeneratedContent(
                title=title,
                text=text,
                platform=platform,
                character_count=len(text)
            )

            self.logger.info(f"✅ Generated {platform} content ({content.character_count} chars)")
            return content

        except ValueError as e:
            # Platform not supported
            self.logger.error(f"❌ Invalid platform: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"❌ Error generating content: {str(e)}")
            raise Exception(f"Content generation failed: {str(e)}")

    def _build_user_message(
        self,
        input_text: str,
        video_transcript: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """Build the user message for content generation"""

        message_parts = [
            "Generate engaging social media content based on the following:",
            "",
            f"**Topic/Input:**",
            input_text,
        ]

        # Add video transcript if provided (highest priority context)
        if video_transcript:
            message_parts.extend([
                "",
                "**Video Transcript (Use this as primary source):**",
                f'"{video_transcript}"',
                "",
                "IMPORTANT: Base your content primarily on this video transcript. Extract key insights, main points, and compelling quotes from the actual spoken content."
            ])

        if additional_context:
            message_parts.extend([
                "",
                f"**Additional Context:**",
                additional_context
            ])

        message_parts.extend([
            "",
            "**Output Format:**",
            "TITLE: [Your engaging title here]",
            "",
            "[Your post text here with proper formatting, bullet points, emojis, hashtags, and community link]",
            "",
            "Make sure to:",
            "- Create an attention-grabbing title",
            "- Write engaging, human-like content (not AI-sounding)",
            "- Use bullet points with → emoji for lists (not other emojis)",
            "- Include the community invitation link naturally in the flow",
            "- Add the required hashtags at the end",
            "- Follow all platform-specific guidelines from the system prompt"
        ])

        return "\n".join(message_parts)

    def _parse_generated_content(self, generated_text: str) -> tuple[str, str]:
        """
        Parse generated text into title and content

        Args:
            generated_text: Raw generated text from AI

        Returns:
            Tuple of (title, text)
        """
        lines = generated_text.strip().split('\n')

        title = ""
        text_lines = []
        found_title = False

        for line in lines:
            # Look for title
            if line.upper().startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
                found_title = True
            elif not found_title and not text_lines:
                # First line might be title without "TITLE:" prefix
                if len(line) < 100 and line.strip():
                    title = line.strip()
                    found_title = True
            else:
                # Everything else is content
                if line.strip():  # Skip empty lines at start
                    text_lines.append(line)

        # Join text
        text = '\n'.join(text_lines).strip()

        # Fallback if no title found
        if not title:
            title = "Engaging Social Media Post"

        # Fallback if no text
        if not text:
            text = generated_text

        return title, text

    def get_supported_platforms(self) -> list[str]:
        """Get list of supported platforms"""
        return ["youtube", "youtube_shorts", "linkedin", "instagram", "tiktok"]

    def validate_platform(self, platform: str) -> bool:
        """Check if platform is supported"""
        return platform.lower() in self.get_supported_platforms()
