"""
Skool Content Generation Service

Handles day-aware content generation for Skool community posts.
Auto-detects the current day of week and uses appropriate prompts.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from src.models.skool import SkoolPostResponse, DAY_TYPES
from src.config import config
from src.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class SkoolContentService:
    """Service for generating day-specific Skool community posts"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Skool Content Service

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.logger = logger

        # Prompts directory
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "skool"

    def get_current_day_type(self) -> str:
        """
        Get the current day type based on day of week

        Returns:
            str: Day type (monday, tuesday, wednesday, thursday, friday, weekend)
        """
        day_of_week = datetime.now().weekday()  # 0 = Monday, 6 = Sunday

        day_mapping = {
            0: "monday",     # Monday
            1: "tuesday",    # Tuesday
            2: "wednesday",  # Wednesday
            3: "thursday",   # Thursday
            4: "friday",     # Friday
            5: "weekend",    # Saturday
            6: "weekend"     # Sunday
        }

        return day_mapping[day_of_week]

    def load_prompt(self, day: str) -> str:
        """
        Load the prompt template for a specific day

        Args:
            day: Day type (monday, tuesday, etc.)

        Returns:
            str: Prompt template content

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = self.prompts_dir / f"{day}.txt"

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}\n"
                f"Available days: monday, tuesday, wednesday, thursday, friday, weekend"
            )

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def build_user_message(
        self,
        topic: str,
        day: str,
        content_details: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Build the user message with topic, content details, and day-specific inputs

        Args:
            topic: Main topic or subject (title/headline)
            day: Day type
            content_details: The full content, story, or details to work with
            inputs: Day-specific inputs (member names, platforms, etc.)
            additional_context: Tone, style, or other requirements

        Returns:
            str: Formatted user message
        """
        message_parts = [
            f"Generate a Skool post for **{DAY_TYPES[day]['name']}**.",
            "",
            f"**Topic/Title:** {topic}",
        ]

        # Add content details if provided (this is the main content source)
        if content_details:
            message_parts.extend([
                "",
                "**Content Details:**",
                content_details,
                "",
                "Use the above details as your primary source material. Shape this into an engaging post following the format guidelines."
            ])

        # Add day-specific inputs if provided
        if inputs:
            message_parts.append("")
            message_parts.append("**Additional Inputs:**")
            for key, value in inputs.items():
                formatted_key = key.replace("_", " ").title()
                message_parts.append(f"- {formatted_key}: {value}")

        # Add additional context if provided (tone, style, constraints)
        if additional_context:
            message_parts.extend([
                "",
                "**Additional Requirements:**",
                additional_context
            ])

        message_parts.extend([
            "",
            "Follow the format and style guidelines from the system prompt.",
            "Generate the post content only - no meta-commentary or explanations."
        ])

        return "\n".join(message_parts)

    def generate_post(
        self,
        topic: str,
        day: Optional[str] = None,
        content_details: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        additional_context: Optional[str] = None
    ) -> SkoolPostResponse:
        """
        Generate a Skool community post

        Args:
            topic: Main topic or subject (title/headline)
            day: Day type (auto-detects if not provided)
            content_details: The full content, story, or details to work with
            inputs: Day-specific inputs
            additional_context: Tone, style, or other requirements

        Returns:
            SkoolPostResponse with generated content

        Raises:
            ValueError: If day type is invalid
            FileNotFoundError: If prompt file doesn't exist
            Exception: If AI generation fails
        """
        try:
            # Auto-detect day if not provided
            if not day:
                day = self.get_current_day_type()
                self.logger.info(f"📅 Auto-detected day type: {day}")
            else:
                day = day.lower()
                if day not in DAY_TYPES:
                    raise ValueError(
                        f"Invalid day type: {day}. "
                        f"Must be one of: {', '.join(DAY_TYPES.keys())}"
                    )

            # Get day metadata
            day_info = DAY_TYPES[day]

            # Load day-specific prompt
            system_prompt = self.load_prompt(day)

            # Build user message
            user_message = self.build_user_message(
                topic=topic,
                day=day,
                content_details=content_details,
                inputs=inputs,
                additional_context=additional_context
            )

            self.logger.info(
                f"🚀 Generating {day_info['name']} for topic: {topic[:50]}..."
            )

            # Get model configuration from YAML (use 'skool' platform if exists, else defaults)
            model_config = config.get_model_config("skool", has_video=False)
            model_name = model_config.get("model", "gpt-4o-mini")
            temperature = model_config.get("temperature", 0.7)

            # Build API call parameters
            api_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": temperature
            }

            # Only include max_tokens if specified
            if "max_tokens" in model_config:
                api_params["max_tokens"] = model_config["max_tokens"]

            # Call OpenAI
            response = self.client.chat.completions.create(**api_params)

            # Extract generated content
            content = response.choices[0].message.content.strip()

            # Calculate stats
            character_count = len(content)
            word_count = len(content.split())

            self.logger.info(
                f"✅ Generated {day_info['name']}: "
                f"{character_count} chars, {word_count} words"
            )

            return SkoolPostResponse(
                success=True,
                day=day,
                post_type=day_info['name'],
                content=content,
                character_count=character_count,
                word_count=word_count,
                model_used=model_name,
                message=f"{day_info['name']} generated successfully"
            )

        except ValueError as e:
            self.logger.error(f"❌ Invalid input: {str(e)}")
            raise

        except FileNotFoundError as e:
            self.logger.error(f"❌ Prompt file error: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"❌ Error generating Skool post: {str(e)}")
            raise Exception(f"Skool post generation failed: {str(e)}")

    def get_day_info(self, day: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific day type

        Args:
            day: Day type (uses current day if not provided)

        Returns:
            dict: Day type metadata
        """
        if not day:
            day = self.get_current_day_type()

        return DAY_TYPES.get(day, {})
