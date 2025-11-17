# Blotato Social Media Automation System

Comprehensive automation suite for managing social media content across 9 platforms using Blotato API, Google Drive integration, AI-powered content generation, and Airtable tracking.

## 🚀 Features

- **REST API**: FastAPI server for on-demand publishing
- **Automated Pipeline**: Scheduled, hands-off operation with APScheduler
- **AI Content Generation**: Platform-specific posts using CrewAI agents
- **Video Transcription**: OpenAI Whisper for better content
- **Multi-Platform**: TikTok, Instagram, LinkedIn, YouTube, Facebook, Twitter, Threads, Bluesky, Pinterest
- **Google Drive Integration**: Auto-monitor folders and upload media
- **Smart Scheduling**: Schedule posts or publish immediately
- **Airtable Database**: Complete tracking with three-table system

## 🔌 Two Ways to Use

### 1. **API Mode** (On-demand) 🆕

FastAPI server for programmatic publishing via HTTP requests.

```bash
# Start the API
uvicorn main:app --reload

# Access at http://localhost:8000/docs
```

**Quick Example:**
```bash
# Post to LinkedIn
curl -X POST http://localhost:8000/posts/text \
  -H "Content-Type: application/json" \
  -d '{"platform": "linkedin", "text": "Hello! 🚀"}'
```

📖 **[Complete API Documentation](docs/API_GUIDE.md)**

### 2. **Automation Mode** (Hands-off)

Scheduled automation that runs continuously:
- Monitors Google Drive folders
- Transcribes videos automatically
- Publishes to missing platforms daily
- Runs 24/7 with APScheduler

```bash
# Run complete pipeline
python automations/daily_automation.py

# Run continuously (8 AM daily, hourly transcription)
python automations/daily_automation.py --continuous
```

## 📦 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file (see `.env.example`):

```env
# Blotato API
BLOTATO_API_KEY=your_blotato_api_key

# Airtable
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id

# Platform Account IDs (from Blotato dashboard)
LINKEDIN_ACCOUNT_ID=abc123
TWITTER_ACCOUNT_ID=def456
INSTAGRAM_ACCOUNT_ID=ghi789
# ... add others as needed

# AI Services (for automations)
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
```

### 3. Get Account IDs

1. Go to https://app.blotato.com
2. Connect your social accounts
3. Copy Account IDs from dashboard
4. Add to `.env` file

### 4. Choose Your Mode

**For API:**
```bash
uvicorn main:app --reload
# Visit http://localhost:8000/docs
```

**For Automations:**
```bash
# Setup Google Drive (first time only)
python automations/setup/setup_blotato_automation.py

# Run pipeline
python automations/daily_automation.py
```

## 📋 System Architecture

### Core Services
- **AirtableService**: Database operations and logging
- **ContentGenerationService**: AI-powered content creation
- **VideoTranscriptionService**: OpenAI Whisper transcription
- **MediaService**: Google Drive and Blotato media handling
- **BlotatoClient**: API communication with rate limiting
- **PublishingService**: Coordinates posting to platforms

### Database Tables (Airtable)

1. **`video-uploads`** - Master record of all uploaded videos
2. **`video-publications`** - Individual platform publications (linked to videos)
3. **`media-logging`** - System logs and error tracking

## 🤖 The 4 Automations

### Automation #1: Folder Monitoring
Upload videos from Google Drive automatically.

```bash
python automations/monitoring/folder_monitor.py
```

### Automation #2: Video Transcription
Transcribe videos using OpenAI Whisper for better content.

```bash
python automations/transcription_automation.py
```

### Automation #3: Smart Publishing
Publish to missing platforms only (smart platform detection).

```bash
# Publish immediately
python automations/publishing/schedule_automation.py

# Schedule for next day at 3 PM
python automations/publishing/schedule_automation.py --schedule
```

### Automation #4: Daily Orchestrator
Complete hands-off automation.

```bash
# Run all 3 automations once
python automations/daily_automation.py

# Run continuously with daily schedule
python automations/daily_automation.py --continuous --schedule
```

## 🎯 Platform Support

| Platform | API Support | Automation Support |
|----------|-------------|-------------------|
| TikTok | ✅ | ✅ |
| Instagram | ✅ | ✅ |
| LinkedIn | ✅ | ✅ |
| Facebook | ✅ | ✅ |
| Twitter (X) | ✅ | ✅ |
| YouTube | ✅ | ✅ |
| Threads | ✅ | ✅ |
| Bluesky | ✅ | ✅ |
| Pinterest | ✅ | ✅ |

## 📁 Project Structure

```
09_blotato/
├── main.py                       # FastAPI server (API routes)
├── automations/                  # Automation scripts
│   ├── daily_automation.py       # Main orchestrator
│   ├── monitoring/               # Google Drive monitoring
│   ├── publishing/               # Publishing automation
│   ├── transcription/            # Video transcription
│   └── setup/                    # Setup scripts
├── src/                          # Core services & models
│   ├── blotato/                  # Blotato API client
│   ├── services/                 # Business logic
│   ├── models/                   # Request/response models
│   ├── prompts/                  # AI prompts per platform
│   ├── utils/                    # Utilities
│   └── config.py                 # Configuration
├── docs/                         # Documentation
│   └── API_GUIDE.md             # Complete API guide
├── prompts/                      # AI prompt templates
├── .env                          # Configuration (create from .env.example)
└── requirements.txt              # Dependencies
```

## 📖 Documentation

- **[API Guide](docs/API_GUIDE.md)** - Complete REST API documentation
- **[.env.example](.env.example)** - Configuration template

## 🔍 Monitoring and Debugging

All operations are logged to Airtable's `media-logging` table with:
- Log levels (INFO, WARNING, ERROR)
- Component tracking
- Full stack traces
- Request/response data
- Session IDs for tracking

Check your Airtable base for detailed logs.

## 💡 Use Cases

**API Mode:**
- Webhooks from other services
- Custom integrations
- Manual publishing
- n8n/Make.com workflows

**Automation Mode:**
- Daily content pipeline
- Automatic Google Drive monitoring
- Scheduled publishing
- Set-and-forget operation

## 🔐 Security

- Never commit `.env` file
- Keep `BLOTATO_API_KEY` secure
- API keys should have minimal required permissions
- Regular backup of Airtable base recommended
- Rate limiting built-in (10 requests/minute)

## 🆘 Support

For issues or questions:
1. Check Airtable `media-logging` table for errors
2. Verify `.env` configuration
3. Test with `/platforms` endpoint
4. Review API docs at http://localhost:8000/docs

## 📄 License

Part of AI Automations Agency project suite.
