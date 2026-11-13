# System Architecture

Clean, flat structure with no unnecessary nesting.

## Directory Structure

```
content-copywriter/
├── main.py                       # FastAPI app: loads .env, includes the routers
│
├── config/
│   └── models.yaml               # OpenAI model settings per platform (read by src/config.py)
│
├── src/                          # Core Business Logic
│   ├── routers/                  # HTTP routes (FastAPI APIRouter per area)
│   │   ├── common_router.py      # GET /, GET /platforms
│   │   ├── blotato_router.py     # /content, /carousel, /media, /posts + validation helpers
│   │   ├── skool_router.py       # POST /skool/post/generate
│   │   └── automation_router.py  # POST /automation/transcribe-video
│   │
│   ├── models/                   # API request/response models
│   │   ├── requests.py           # TextPostRequest, MediaPostRequest, BulkPostRequest
│   │   ├── responses.py          # PostResponse, MediaUploadResponse, BulkPostResponse
│   │   ├── content.py            # ContentGenerationRequest/Response
│   │   ├── carousel.py           # Carousel request/response models
│   │   └── skool.py              # SkoolPostRequest/Response
│   │
│   ├── blotato/                  # Blotato API client
│   │   ├── client.py             # HTTP client for Blotato API
│   │   ├── models.py             # Blotato data models
│   │   └── exceptions.py         # Custom exceptions
│   │
│   ├── services/                 # Business logic services
│   │   ├── ai_content_service.py         # AI content generation (OpenAI)
│   │   ├── publishing_service.py         # Post publishing logic
│   │   ├── airtable_service.py           # Database operations
│   │   ├── media_service.py              # Google Drive handling
│   │   ├── video_transcription_service.py # Video transcription
│   │   ├── content_generation_service.py  # CrewAI content (automations)
│   │   ├── content_service.py            # Upload from Drive + publish in one call
│   │   └── skool_content_service.py      # Skool post generation
│   │
│   ├── prompts/                  # Platform-specific AI prompts
│   │   ├── youtube_shorts.py     # YouTube Shorts prompts
│   │   ├── linkedin.py           # LinkedIn prompts
│   │   ├── instagram.py          # Instagram prompts
│   │   └── tiktok.py             # TikTok prompts
│   │
│   ├── utils/                    # Utilities
│   │   ├── logger.py             # Logging setup
│   │   ├── google_drive.py       # Google Drive utilities
│   │   └── url_converter.py      # Google Drive share URL -> direct download URL
│   │
│   └── config.py                 # Central configuration
│
├── automations/                  # Automation scripts
│   ├── daily_automation.py       # Main orchestrator
│   ├── monitoring/               # Google Drive monitoring
│   ├── publishing/               # Publishing automation
│   ├── transcription/            # Video transcription
│   └── setup/                    # Setup scripts
│
└── docs/                         # Documentation
    ├── API_GUIDE.md              # Complete API documentation
    └── ARCHITECTURE.md           # This file
```

## Design Principles

### 1. Flat Structure
- No unnecessary nesting (`api/` folder removed)
- `main.py` at root level
- Easy to navigate and understand

### 2. Single Source of Truth
- All business logic in `src/`
- All models in `src/models/`
- No duplication between API and automations

### 3. Clear Separation
- `main.py` - creates the FastAPI app and includes the routers
- `src/routers/` - HTTP routes + validation helpers
- `src/services/` - All business logic
- `src/models/` - All data models
- `automations/` - Orchestration scripts

## Layer Responsibilities

### API Server (`main.py` + `src/routers/`)
- **Purpose**: HTTP interface for external access
- **Contains**: `main.py` loads `.env` and includes the four routers; each router in `src/routers/` holds its routes and validation helpers
- **Does NOT contain**: Business logic
- **Uses**: `src/services/` and `src/models/`

### Core (`src/`)
- **Purpose**: Reusable business logic and models
- **Contains**: All services, models, utilities, configs
- **Used by**: the routers, automation scripts, any consumers

### Automations (`automations/`)
- **Purpose**: Scheduled, hands-off workflows
- **Contains**: Orchestration scripts
- **Uses**: `src/services/` for all business logic

## Data Flow

### API Request Flow
```
HTTP Request
    ↓
main.py (FastAPI app)
    ↓
src/routers/ (route + validation helpers)
    ↓
src/services/ (business logic)
    ↓
src/blotato/client.py (external API)
    ↓
Blotato API
```

### Automation Flow
```
automations/daily_automation.py
    ↓
src/services/ (same business logic)
    ↓
src/blotato/client.py
    ↓
Blotato API
```

## Module Organization

### Models (`src/models/`)
All API-facing data models:
- **requests.py** - Request models (TextPostRequest, etc.)
- **responses.py** - Response models (PostResponse, etc.)
- **content.py** - Content generation models
- **carousel.py** - Carousel generation and publishing models
- **skool.py** - Skool post generation models

### Services (`src/services/`)
All business logic:
- **publishing_service.py** - Post publishing to platforms
- **ai_content_service.py** - OpenAI content generation
- **content_generation_service.py** - CrewAI content (automations)
- **airtable_service.py** - Database operations
- **media_service.py** - Google Drive integration
- **video_transcription_service.py** - Video transcription
- **content_service.py** - Upload media from Google Drive and publish it in one call
- **skool_content_service.py** - Skool post generation (used by `/skool/post/generate`)

### Prompts (`src/prompts/`)
Platform-specific AI prompts (Python modules):
- Shared by both AI services
- One file per platform
- Easy to update and version control

### Configuration (`src/config.py`)
Central configuration:
- Environment variables
- Platform settings
- Account IDs
- Supported platforms list

## Import Pattern

### From main.py
```python
# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import services
from services.publishing_service import PublishingService
from services.ai_content_service import AIContentService

# Import models
from models.requests import TextPostRequest
from models.responses import PostResponse

# Import config
from config import config
```

### From automations
```python
# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Same imports as main.py
from services.publishing_service import PublishingService
```

## Why This Structure?

### ✅ Before (nested)
```
api/
├── main.py
├── models/...
└── services/... (wrappers)

src/
├── services/... (real logic)
└── ...
```
- Confusing duplication
- Extra nesting
- Unclear where things belong

### ✅ After (flat)
```
main.py              # FastAPI app, includes the routers
src/
├── routers/...      # API routes
├── models/...       # All models
└── services/...     # All logic
```
- Clear structure
- No duplication
- Easy to understand

## Running the API

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Adding New Features

1. **New model?** → Add to `src/models/`
2. **New service?** → Add to `src/services/`
3. **New endpoint?** → Add a route to the matching router in `src/routers/` (a new router is exported from `src/routers/__init__.py` and needs `app.include_router(...)` in `main.py`)
4. **New platform?** → Add prompt to `src/prompts/`

Everything lives in `src/` and can be used by both API and automations!
