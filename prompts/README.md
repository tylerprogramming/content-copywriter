# Platform Prompts

This folder contains platform-specific prompts for AI content generation as **text files**.

## Structure

Each platform has its own prompt file that defines:
- Writing style guidelines
- Content structure
- Engagement tactics
- Required elements (community links, hashtags)
- Platform-specific best practices

## Prompt Files

### LinkedIn
- **`linkedin_text.txt`** - Used for text-only LinkedIn posts
- **`linkedin_video.txt`** - Used when generating LinkedIn posts from YouTube videos

### Other Platforms
- **`youtube_shorts.txt`** - YouTube Shorts captions
- **`instagram.txt`** - Instagram post/reel captions
- **`tiktok.txt`** - TikTok video captions

## How It Works

The prompts are loaded automatically by `src/prompts/__init__.py`:

```python
from prompts import get_prompt

# Get standard LinkedIn prompt
prompt = get_prompt("linkedin")

# Get LinkedIn video-specific prompt
prompt = get_prompt("linkedin", has_video=True)
```

## Editing Prompts

Simply edit the `.txt` files in this folder. Changes take effect on the next API restart.

**Example:** To customize LinkedIn video posts, edit `linkedin_video.txt`

## Adding New Platforms

1. Create a new prompt file: `prompts/new_platform.txt`
2. Update `src/prompts/__init__.py` to include the new platform
3. Add the platform to supported lists in services and config

## Tips

- Keep prompts clear and specific
- Include examples where helpful
- Define banned words/phrases
- Specify required elements (hashtags, links)
- Use consistent structure across platforms
