"""
Skool Post Generation Models

Request and response models for the Skool community post generation API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class SkoolPostRequest(BaseModel):
    """
    Request model for generating Skool community posts

    The API auto-detects the current day of week and uses the appropriate prompt.
    You can override this by specifying a 'day' parameter.

    **How to structure your request:**

    - **topic**: The title/headline/subject (required)
    - **content_details**: The full content, story, or details (optional but recommended)
    - **additional_context**: Tone, style, or other requirements (optional)

    **Examples:**

    Monday (Value Post):
    ```
    {
      "topic": "3 things every AI Agent should have",
      "content_details": "1) Error handling with exponential backoff - catches API failures and retries intelligently. 2) Structured logging using JSON format - makes debugging 10x easier. 3) State persistence with Redis - tracks progress across runs so you can resume."
    }
    ```

    Wednesday (Personal Story):
    ```
    {
      "topic": "When I over-engineered my automation",
      "content_details": "I spent 2 weeks building a custom state manager for my AI agents. Created a whole PostgreSQL system with tables for tracking which APIs were called. Then I read the CrewAI Flows docs more carefully and realized it handles state automatically. Total facepalm moment.",
      "additional_context": "Make it vulnerable and relatable"
    }
    ```

    Friday (Community Win):
    ```
    {
      "topic": "Community wins this week",
      "content_details": "Sarah just connected Airtable to CrewAI to generate daily leads automatically. She went from manually entering 50 leads a day to having it all automated.",
      "inputs": {
        "member_name": "Sarah",
        "achievement": "automated lead generation"
      }
    }
    ```
    """

    topic: str = Field(
        ...,
        description="Title, headline, or main subject of the post",
        min_length=10,
        examples=["3 things every AI Agent should have", "When I over-engineered my automation"]
    )

    content_details: Optional[str] = Field(
        None,
        description="The full content, story, details, or main points you want to include. This is your raw material that the AI will shape into an engaging post.",
        examples=[
            "1) Error handling with retries 2) Structured logging 3) State management",
            "I spent 2 weeks building a custom solution before finding it was already built-in..."
        ]
    )

    day: Optional[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "weekend"]] = Field(
        None,
        description="Override the day-specific prompt. If not provided, uses current day of week."
    )

    inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Day-specific inputs (member names, results, platforms, etc.)",
        examples=[{
            "member_name": "Sarah",
            "result": "built first CrewAI flow in 48 hours",
            "platform": "YouTube"
        }]
    )

    additional_context: Optional[str] = Field(
        None,
        description="Tone, style, constraints, or other requirements (e.g., 'Make it beginner-friendly', 'Keep it under 300 words')"
    )


class SkoolPostResponse(BaseModel):
    """Response model for generated Skool post"""

    success: bool = Field(description="Whether generation was successful")

    day: str = Field(
        description="Day type used (monday, tuesday, etc.)"
    )

    post_type: str = Field(
        description="Human-readable post type (e.g., 'Value-Driven Post', 'Community Post')"
    )

    content: str = Field(
        description="Generated post content ready to publish"
    )

    character_count: int = Field(
        description="Total character count of the generated post"
    )

    word_count: int = Field(
        description="Total word count of the generated post"
    )

    model_used: str = Field(
        description="AI model used for generation (from YAML config)"
    )

    message: str = Field(
        description="Status message or additional info"
    )

    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when content was generated"
    )


# Day type metadata for documentation and UI
DAY_TYPES = {
    "monday": {
        "name": "Value-Driven Post",
        "description": "Teaching post with actionable tips",
        "required_inputs": ["topic"],
        "optional_inputs": []
    },
    "tuesday": {
        "name": "Offer Post",
        "description": "Showcase paid community value",
        "required_inputs": ["topic"],
        "optional_inputs": ["member_name", "result", "pain_point", "paid_group_name"]
    },
    "wednesday": {
        "name": "Personal Story",
        "description": "Behind-the-scenes lessons and experiences",
        "required_inputs": ["topic"],
        "optional_inputs": []
    },
    "thursday": {
        "name": "Cross-Platform Share",
        "description": "Repurpose content from YouTube/LinkedIn/X",
        "required_inputs": ["topic"],
        "optional_inputs": ["platform", "content_topic", "link", "question"]
    },
    "friday": {
        "name": "Community Wins",
        "description": "Celebrate member achievements",
        "required_inputs": ["topic"],
        "optional_inputs": ["member_name", "achievement", "action_others_can_take"]
    },
    "weekend": {
        "name": "Off-Topic/Personal",
        "description": "Lighthearted connection and conversation",
        "required_inputs": ["topic"],
        "optional_inputs": []
    }
}
