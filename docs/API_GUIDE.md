# Blotato Social Media API Guide

FastAPI server for publishing content to 9 social media platforms via Blotato API.

## Quick Start

### 1. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload
```

Server runs at: **http://localhost:8000**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Get Your Blotato Credentials

**Get API Key:**
1. Go to https://app.blotato.com
2. Settings → API Keys
3. Copy your API key

**Connect Social Accounts & Get Account IDs:**
1. Blotato Dashboard → **Connected Accounts**
2. Click **"Connect Account"** for each platform
3. Copy each Account ID after connecting

### 3. Configure Environment

Update `.env`:
```env
BLOTATO_API_KEY=your_api_key_here

# Add account IDs for platforms you connected
LINKEDIN_ACCOUNT_ID=abc123
TWITTER_ACCOUNT_ID=def456
INSTAGRAM_ACCOUNT_ID=ghi789
# ... etc
```

## Supported Platforms

| # | Platform | Key | .env Variable |
|---|----------|-----|---------------|
| 1 | TikTok | `tiktok` | `TIKTOK_ACCOUNT_ID` |
| 2 | Instagram | `instagram` | `INSTAGRAM_ACCOUNT_ID` |
| 3 | LinkedIn | `linkedin` | `LINKEDIN_ACCOUNT_ID` |
| 4 | Facebook | `facebook` | `FACEBOOK_ACCOUNT_ID` |
| 5 | Twitter (X) | `twitter` | `TWITTER_ACCOUNT_ID` |
| 6 | YouTube | `youtube` | `YOUTUBE_ACCOUNT_ID` |
| 7 | Threads | `threads` | `THREADS_ACCOUNT_ID` |
| 8 | Bluesky | `bluesky` | `BLUESKY_ACCOUNT_ID` |
| 9 | Pinterest | `pinterest` | `PINTEREST_ACCOUNT_ID` |

## API Endpoints

### 0. AI Content Generation (NEW!)

Generate platform-optimized social media content using AI.

```bash
POST /content/generate
```

**Supported Platforms for AI Generation:**
- `youtube` or `youtube_shorts` - YouTube Shorts captions
- `linkedin` - Professional LinkedIn posts
- `instagram` - Instagram captions for posts/reels
- `tiktok` - TikTok video captions

**Request:**
```json
{
  "platform": "linkedin",
  "input_text": "AI agents can automate 80% of customer support tickets, saving businesses time and money",
  "additional_context": "Focus on benefits for small businesses"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "input_text": "AI agents revolutionize customer service by automating 80% of support tickets"
  }'
```

**Response:**
```json
{
  "success": true,
  "platform": "linkedin",
  "title": "AI Agents Are Transforming Customer Service",
  "text": "80% of support tickets can now be automated with AI agents.\n\nHere's what that means for your business:\n\n👉 Faster response times for customers\n👉 Lower operational costs\n👉 24/7 availability\n👉 Consistent service quality\n\nJoin our free community of AI agency builders at https://www.skool.com/the-ai-agency-5370/about\n\n#ai #aiautomation #automation #aiagent",
  "character_count": 312,
  "message": "Content generated successfully for linkedin"
}
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/content/generate",
    json={
        "platform": "instagram",
        "input_text": "5 ways AI is changing the game for content creators",
        "additional_context": "Keep it fun and engaging"
    }
)

content = response.json()
print(f"Title: {content['title']}")
print(f"Text:\n{content['text']}")
print(f"Character count: {content['character_count']}")
```

### Check Configuration

```bash
GET /platforms
```

Returns supported platforms and which ones are configured.

```bash
curl http://localhost:8000/platforms
```

### 1. Text Post

Publish text-only content to a platform.

```bash
POST /posts/text
```

**Request:**
```json
{
  "platform": "linkedin",
  "text": "Check out this post! 🚀",
  "scheduled_time": null  // Optional: ISO 8601 datetime
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/posts/text \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "text": "Hello from the API! 🚀"
  }'
```

**Response:**
```json
{
  "success": true,
  "platform": "linkedin",
  "submission_id": "abc123",
  "message": "Post published successfully to linkedin",
  "scheduled_time": null
}
```

### 2. Media Upload

Upload media (image/video) to get a media URL.

```bash
POST /media/upload
```

**Example:**
```bash
curl -X POST http://localhost:8000/media/upload \
  -F "file=@video.mp4"
```

**Response:**
```json
{
  "success": true,
  "media_url": "https://cdn.blotato.com/media/xyz789.mp4",
  "message": "Media uploaded successfully: video.mp4"
}
```

### 3. Media Post

Publish content with media (use media URL from `/media/upload`).

```bash
POST /posts/media
```

**Request:**
```json
{
  "platform": "instagram",
  "text": "Check out this video! 🎥",
  "media_url": "https://cdn.blotato.com/media/xyz789.mp4",
  "scheduled_time": null
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/posts/media \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "text": "Amazing content! 🎥",
    "media_url": "https://cdn.blotato.com/media/xyz789.mp4"
  }'
```

### 4. Bulk Post

Publish the same content to multiple platforms at once.

```bash
POST /posts/bulk
```

**Request:**
```json
{
  "platforms": ["linkedin", "twitter", "facebook"],
  "text": "Multi-platform announcement! 📢",
  "media_url": null,  // Optional
  "scheduled_time": null
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/posts/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["linkedin", "twitter"],
    "text": "Big news! 🎉"
  }'
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "platform": "linkedin",
      "submission_id": "abc123",
      "message": "Published successfully to linkedin"
    },
    {
      "success": true,
      "platform": "twitter",
      "submission_id": "def456",
      "message": "Published successfully to twitter"
    }
  ],
  "summary": {
    "total": 2,
    "successful": 2,
    "failed": 0
  }
}
```

## Scheduling Posts

To schedule a post for future publishing, include `scheduled_time` in ISO 8601 format:

```bash
curl -X POST http://localhost:8000/posts/text \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "text": "Scheduled for tomorrow! ⏰",
    "scheduled_time": "2025-11-06T15:00:00Z"
  }'
```

**Python Example:**
```python
from datetime import datetime, timedelta

scheduled_time = datetime.now() + timedelta(days=1)
scheduled_time = scheduled_time.replace(hour=15, minute=0)

response = requests.post(
    "http://localhost:8000/posts/text",
    json={
        "platform": "linkedin",
        "text": "Scheduled post!",
        "scheduled_time": scheduled_time.isoformat()
    }
)
```

## Complete Workflow Example

### AI-Generated Content → Publish to Multiple Platforms

```python
import requests

API = "http://localhost:8000"

# Step 1: Generate content for LinkedIn
content_response = requests.post(
    f"{API}/content/generate",
    json={
        "platform": "linkedin",
        "input_text": "AI automation is helping small businesses compete with enterprise companies"
    }
)

linkedin_content = content_response.json()
print(f"Generated: {linkedin_content['title']}")

# Step 2: Publish to LinkedIn
linkedin_response = requests.post(
    f"{API}/posts/text",
    json={
        "platform": "linkedin",
        "text": linkedin_content['text']
    }
)

print(f"Published to LinkedIn: {linkedin_response.json()['submission_id']}")

# Step 3: Generate Instagram version
instagram_content_response = requests.post(
    f"{API}/content/generate",
    json={
        "platform": "instagram",
        "input_text": "AI automation is helping small businesses compete with enterprise companies"
    }
)

instagram_content = instagram_content_response.json()

# Step 4: Publish to Instagram
instagram_response = requests.post(
    f"{API}/posts/text",
    json={
        "platform": "instagram",
        "text": instagram_content['text']
    }
)

print(f"Published to Instagram: {instagram_response.json()['submission_id']}")
```

## Python Usage Examples

### AI Content Generation
```python
import requests

# Generate LinkedIn content
response = requests.post(
    "http://localhost:8000/content/generate",
    json={
        "platform": "linkedin",
        "input_text": "5 AI automation mistakes that cost businesses thousands"
    }
)

content = response.json()
print(content['text'])
```

### Text Post
```python
import requests

response = requests.post(
    "http://localhost:8000/posts/text",
    json={
        "platform": "linkedin",
        "text": "Hello from Python! 🐍"
    }
)
print(response.json())
```

### Media Post (Complete Workflow)
```python
import requests

API = "http://localhost:8000"

# Step 1: Upload media
with open("video.mp4", "rb") as f:
    upload = requests.post(f"{API}/media/upload", files={"file": f})

media_url = upload.json()["media_url"]

# Step 2: Post with media
response = requests.post(
    f"{API}/posts/media",
    json={
        "platform": "instagram",
        "text": "Check this out! 🎥",
        "media_url": media_url
    }
)
print(response.json())
```

### Bulk Post
```python
import requests

response = requests.post(
    "http://localhost:8000/posts/bulk",
    json={
        "platforms": ["linkedin", "twitter", "facebook"],
        "text": "Multi-platform announcement! 📢"
    }
)
print(response.json())
```

## How It Works

### Architecture
```
Your App
  ↓
Your FastAPI Server (localhost:8000)
  ↓
api/main.py → Routes
  ↓
api/services/ → Business Logic
  ↓
src/services/publishing_service.py
  ↓
src/blotato/client.py
  ↓
Blotato API (backend.blotato.com)
  ↓
Social Media Platforms
```

### Text Post Flow
```
1. POST http://localhost:8000/posts/text
   {"platform": "linkedin", "text": "Hello!"}

2. FastAPI validates request

3. PostService validates platform & gets account ID from .env

4. PublishingService creates Blotato API request

5. BlotatoClient posts to:
   POST https://backend.blotato.com/v2/posts

6. Blotato publishes to LinkedIn

7. Returns submission ID
```

### Media Post Flow
```
1. Upload Media:
   POST /media/upload → Returns media_url

2. Publish with Media:
   POST /posts/media with media_url

3. Same flow as text post, but includes media
```

## Error Handling

### Platform Not Configured
```json
{
  "detail": "Platform 'tiktok' not configured. Please add TIKTOK_ACCOUNT_ID to .env file"
}
```
**Fix:** Add the platform's account ID to `.env` and restart server.

### Invalid Platform
```json
{
  "detail": "Unsupported platform: myspace. Supported: tiktok, facebook, ..."
}
```
**Fix:** Use a valid platform key (lowercase).

### Blotato API Error
```json
{
  "detail": "API error: Invalid account ID"
}
```
**Fix:** Verify account ID is correct in Blotato dashboard.

## Troubleshooting

**"Module not found" errors**
- Run `pip install -r requirements.txt`
- Ensure you're in `09_blotato` directory

**"Platform not configured"**
- Add `PLATFORM_ACCOUNT_ID` to `.env`
- Restart server: `uvicorn api.main:app --reload`

**Media upload fails**
- Check file size (max 200MB)
- Verify supported format (mp4, jpg, png, etc.)

**Import errors**
- Verify all dependencies installed
- Check Python path includes project root

## Production Deployment

```bash
# Using uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing

Run the test suite:
```bash
python api/test_api.py
```

Or test manually with cURL commands above.

## Integration with Automations

This API complements the automation system:
- **Automations** (`automations/`) - Scheduled, hands-off operation
- **API** (`api/`) - On-demand, programmatic access

Both use the same core services and configuration.
