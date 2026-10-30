#!/usr/bin/env python3
"""
Content Generation Service using CrewAI
Platform-specific post text and title generation using AI agents
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from crewai import Agent, LLM
from src.utils.logger import setup_logger
from src.config import config

from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

class PostContent(BaseModel):
    """Structured post content response"""
    title: str = Field(description="Engaging title/headline for the post")
    text: str = Field(description="Main post content with appropriate hashtags and emojis")
    hashtags: list[str] = Field(description="List of relevant hashtags")
    platform_optimized: bool = Field(description="Whether content is optimized for the target platform")
    character_count: int = Field(description="Total character count of the post text")
    estimated_engagement: str = Field(description="Predicted engagement level (High/Medium/Low)")

class ContentGenerationService:
    """Service for generating platform-specific content using CrewAI agents"""
    
    def __init__(self):
        self.logger = logger
        self._agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize CrewAI agents for different platforms"""
        
        # Social Media Content Creator Agent
        self.content_creator = Agent(
            role="Expert Social Media Content Creator",
            goal="Create engaging, platform-specific content that drives maximum engagement and aligns with brand voice",
            backstory="""You are a seasoned social media expert with years of experience creating viral content 
            across all major platforms. You understand the nuances of each platform's algorithm, audience behavior, 
            and optimal posting strategies. You excel at crafting content that not only engages but also converts.""",
            tools=[],
            verbose=False,
            allow_delegation=False,
            llm=LLM(model="gpt-5.6-sol")
        )
        
        logger.info("✅ CrewAI Content Generation Agent initialized")
    
    def _load_platform_prompts(self, platform: str) -> Dict[str, str]:
        """Load platform-specific prompts from files"""
        prompts_dir = "prompts"
        platform_file = f"{prompts_dir}/{platform.lower()}_prompts.txt"
        
        try:
            if os.path.exists(platform_file):
                with open(platform_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse sections (assuming format: [SECTION_NAME] content)
                sections = {}
                current_section = None
                current_content = []
                
                for line in content.split('\n'):
                    if line.strip().startswith('[') and line.strip().endswith(']'):
                        if current_section:
                            sections[current_section] = '\n'.join(current_content).strip()
                        current_section = line.strip()[1:-1].lower()
                        current_content = []
                    else:
                        current_content.append(line)
                
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                return sections
            else:
                logger.warning(f"Platform prompt file not found: {platform_file}")
                return self._get_default_prompts(platform)
                
        except Exception as e:
            logger.error(f"Error loading prompts for {platform}: {str(e)}")
            return self._get_default_prompts(platform)
    
    def _get_default_prompts(self, platform: str) -> Dict[str, str]:
        """Get default prompts for platforms without custom prompt files"""
        return {
            "system": f"You are an expert {platform} content creator.",
            "content_guidelines": f"Create engaging content optimized for {platform} audience and algorithm.",
            "format_requirements": "Include relevant hashtags and emojis appropriate for the platform."
        }
    
    def generate_post_content(self, 
                            platform: str, 
                            video_context: str = None,
                            video_transcription: str = None,
                            brand_voice: str = "professional yet engaging",
                            target_audience: str = "business professionals and entrepreneurs",
                            additional_context: str = None) -> PostContent:
        """
        Generate platform-specific post content using CrewAI agent
        
        Args:
            platform: Target platform (tiktok, instagram, linkedin, etc.)
            video_context: Description of the video content
            video_transcription: Full transcript of the video content
            brand_voice: Brand voice/tone to use
            target_audience: Target audience description
            additional_context: Any additional context or requirements
            
        Returns:
            PostContent: Structured post content optimized for the platform
        """
        try:
            logger.info(f"🚀 Generating content for {platform}")
            
            # Load platform-specific prompts
            prompts = self._load_platform_prompts(platform)
            
            # Build comprehensive prompt
            prompt = self._build_generation_prompt(
                platform=platform,
                video_context=video_context,
                video_transcription=video_transcription,
                brand_voice=brand_voice,
                target_audience=target_audience,
                additional_context=additional_context,
                prompts=prompts
            )
            
            logger.info(f"📝 Sending prompt to CrewAI agent...")
            
            # Generate content using CrewAI agent
            result = self.content_creator.kickoff(
                prompt,
                response_format=PostContent
            )
            
            # Extract structured content
            if result.pydantic:
                content = result.pydantic
                logger.info(f"✅ Generated content for {platform}")
                logger.info(f"📊 Character count: {content.character_count}")
                logger.info(f"🎯 Estimated engagement: {content.estimated_engagement}")
                return content
            else:
                # Fallback: parse raw response
                logger.warning("⚠️  No structured output, parsing raw response")
                return self._parse_raw_response(result.raw, platform)
                
        except Exception as e:
            logger.error(f"❌ Error generating content for {platform}: {str(e)}")
            return self._create_fallback_content(platform, video_context)
    
    def _build_generation_prompt(self, 
                               platform: str, 
                               video_context: str,
                               video_transcription: str, 
                               brand_voice: str, 
                               target_audience: str, 
                               additional_context: str, 
                               prompts: Dict[str, str]) -> str:
        """Build comprehensive content generation prompt"""
        
        prompt_parts = [
            f"PLATFORM: {platform.upper()}",
            f"BRAND VOICE: {brand_voice}",
            f"TARGET AUDIENCE: {target_audience}",
            "",
            "TASK: Create engaging post content optimized for this specific platform.",
            "",
            "PLATFORM-SPECIFIC REQUIREMENTS:",
            prompts.get('format_requirements', f'Optimize for {platform} best practices'),
            "",
            "CONTENT GUIDELINES:",
            prompts.get('content_guidelines', 'Create engaging, authentic content'),
        ]
        
        # Add video transcription (highest priority content source)
        if video_transcription:
            prompt_parts.extend([
                "",
                "VIDEO TRANSCRIPT:",
                f"The following is the complete transcript of the video content:",
                f'"{video_transcription}"',
                "",
                "IMPORTANT: Base your post content primarily on this transcript. Extract key insights, main points, and compelling quotes. The transcript contains the actual spoken content, so use it to create accurate and engaging social media posts."
            ])
        elif video_context:
            prompt_parts.extend([
                "",
                "VIDEO CONTEXT:",
                f"The video content is about: {video_context}",
                "Base your post content on this video context while making it platform-appropriate."
            ])
        
        if additional_context:
            prompt_parts.extend([
                "",
                "ADDITIONAL CONTEXT:",
                additional_context
            ])
        
        # Platform-specific requirements
        if platform.lower() in ["linkedin", "tiktok", "instagram"]:
            comment_instruction = """
SPECIAL INSTRUCTION: If the transcript mentions saying "COMMENT 'something'" or asks people to comment a specific word/phrase, start the FIRST LINE with that exact call-to-action (e.g., "Comment 'SCALE' if you're ready to grow your business!").
"""
        else:
            comment_instruction = ""
            
        prompt_parts.extend([
            "",
            comment_instruction,
            "CONTENT STYLE REQUIREMENTS:",
            "- Write like a HUMAN, not an AI - avoid robotic language",
            "- Use bullet points with 👉 emoji (not other emojis for bullets)", 
            "- Format as a list of specific benefits/tips that help them",
            "- Keep it conversational and authentic",
            "- Avoid phrases like 'dive deep', 'game-changer', 'unlock potential', etc.",
            "",
            "COMMUNITY ENGAGEMENT:",
            "After the bullet points, naturally include:",
            "\"Join our free community of AI agency builders at https://www.skool.com/the-ai-agency/about\"",
            "",
            "OUTPUT REQUIREMENTS:",
            "- Write engaging post text in bullet format with 👉 emojis",
            "- Include community invitation after bullet points",
            "- Sound human and conversational, not AI-generated",
            "- Keep within platform character limits",
            "- ONLY use these hashtags at the end: #ai #aiautomation #automation #aiagent",
            "- NO YouTube comment calls-to-action (even if in transcript)"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_raw_response(self, raw_response: str, platform: str) -> PostContent:
        """Parse raw response into structured content (fallback method)"""
        try:
            # Simple parsing logic for fallback
            title = "Engaging Content"
            text = raw_response[:280] if platform == "twitter" else raw_response[:2000]
            hashtags = ["#content", f"#{platform}", "#automation"]
            
            # Use only approved hashtags
            hashtags = ["#ai", "#aiautomation", "#automation", "#aiagent"]
            
            return PostContent(
                title=title,
                text=text,
                hashtags=hashtags,
                platform_optimized=True,
                character_count=len(text),
                estimated_engagement="Medium"
            )
        except Exception as e:
            logger.error(f"Error parsing raw response: {str(e)}")
            return self._create_fallback_content(platform, "AI-generated content")
    
    def _create_fallback_content(self, platform: str, context: str = None) -> PostContent:
        """Create basic fallback content if AI generation fails"""
        
        # Approved hashtags only
        approved_hashtags = ["#ai", "#aiautomation", "#automation", "#aiagent"]
        
        fallback_templates = {
            "tiktok": {
                "title": "AI Automation Content!",
                "text": "👉 Check out this amazing AI automation content!\n\nJoin our free community of AI agency builders at https://www.skool.com/the-ai-agency-5370/about",
                "hashtags": approved_hashtags
            },
            "instagram": {
                "title": "AI Content Drop!",
                "text": "👉 New AI automation insights just dropped!\n\nJoin our free community of AI agency builders at https://www.skool.com/the-ai-agency-5370/about",
                "hashtags": approved_hashtags
            },
            "linkedin": {
                "title": "AI Automation Insights",
                "text": "👉 Sharing valuable AI automation insights with my network\n\nJoin our free community of AI agency builders at https://www.skool.com/the-ai-agency-5370/about",
                "hashtags": approved_hashtags
            },
            "youtube": {
                "title": "AI Automation Content",
                "text": "👉 Check out this AI automation content!\n\nJoin our free community of AI agency builders at https://www.skool.com/the-ai-agency-5370/about",
                "hashtags": approved_hashtags
            }
        }
        
        template = fallback_templates.get(platform.lower(), fallback_templates["instagram"])
        
        if context:
            template["text"] = f"Check out this content about {context}! " + template["text"]
        
        logger.warning(f"⚠️  Using fallback content for {platform}")
        
        return PostContent(
            title=template["title"],
            text=template["text"],
            hashtags=template["hashtags"],
            platform_optimized=True,
            character_count=len(template["text"]),
            estimated_engagement="Medium"
        )
    
    def get_supported_platforms(self) -> list[str]:
        """Get list of supported platforms"""
        return config.SUPPORTED_PLATFORMS
    
    def validate_platform(self, platform: str) -> bool:
        """Validate if platform is supported"""
        return platform.lower() in [p.lower() for p in self.get_supported_platforms()]