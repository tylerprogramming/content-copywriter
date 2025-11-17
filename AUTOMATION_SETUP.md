# Google Drive to Blotato Automation Setup

This automation processes MP4 videos from Google Drive and uploads them to Blotato with Airtable tracking.

## 📋 Workflow Overview

1. **List MP4 files** in `media_not_uploaded` folder (Google Drive)
2. **Upload each file** to Blotato
3. **Create Airtable record** in `video-uploads` table with:
   - Google Drive URL
   - Google Drive File ID
   - Blotato Media URL
   - Upload Status: "Success"
   - Upload Time
4. **Move file** to `media_uploaded` folder (Google Drive)
5. **Set transcription status** to "Pending" (transcription done separately)

---

## 🛠️ Setup Instructions

### 1. Install Required Packages

```bash
pip install composio-core composio-openai openai pyairtable apify-client
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Composio (for Google Drive)
COMPOSIO_API_KEY=your_composio_api_key_here

# OpenAI (required by Composio)
OPENAI_API_KEY=your_openai_api_key_here

# Blotato
BLOTATO_API_KEY=your_blotato_api_key_here

# Airtable
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=appRcimSdzB4syDWp

# Apify (for video transcription - optional)
APIFY_API_TOKEN=your_apify_token_here
```

### 3. Get Your Composio API Key

1. Go to [composio.dev](https://composio.dev)
2. Sign up / Log in
3. Navigate to API Keys section
4. Copy your API key
5. Paste it in `.env` file

### 4. Connect Google Drive to Composio

```bash
# Install Composio CLI
pip install composio-core

# Login to Composio
composio login

# Connect Google Drive for your user
composio add googledrive --user-id pg-dev-tylerai-blotato
```

This will open a browser window to authorize Google Drive access.

---

## 🚀 Usage

### Method 1: API Endpoint

Start your FastAPI server:

```bash
uvicorn main:app --reload
```

Then call the automation endpoint:

```bash
curl -X POST "http://localhost:8000/automation/drive-to-blotato" \
  -H "Content-Type: application/json" \
  -d '{
    "source_folder_id": "1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ",
    "processed_folder_id": "1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu"
  }'
```

**Response:**
```json
{
  "success": true,
  "files_processed": 3,
  "files_failed": 0,
  "total_files": 3,
  "results": [
    {
      "success": true,
      "file_id": "1AbC...",
      "file_name": "video1.mp4",
      "google_drive_url": "https://drive.google.com/file/d/...",
      "blotato_media_url": "https://database.blotato.io/...",
      "airtable_record_id": "rec123..."
    }
  ]
}
```

### Method 2: Python Script

```python
from src.services.drive_media_workflow_service import DriveMediaWorkflowService

# Initialize service
service = DriveMediaWorkflowService(
    source_folder_id="1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ",  # media_not_uploaded
    processed_folder_id="1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu"  # media_uploaded
)

# Process folder
result = service.process_folder()

print(f"Processed {result['files_processed']} files")
```

---

## 📊 Airtable Structure

### Table: `video-uploads`

| Field | Type | Description |
|-------|------|-------------|
| Google Drive URL | URL | Original Google Drive share link |
| Google Drive File ID | Single line text | File ID extracted from URL |
| Converted URL | URL | Direct download URL |
| Blotato Media URL | URL | Uploaded media URL from Blotato |
| Upload Status | Single select | Success, Failed, Processing |
| Upload Time | Date | When upload completed |
| Error Message | Long text | Error details if upload failed |
| Transcription | Long text | Video transcription text |
| Transcription Status | Single select | Pending, Processing, Complete, Failed |
| video-publications | Linked records | Links to video-publications table |

---

## 🎬 Video Transcription (Separate Step)

Transcription requires a YouTube URL since we can't directly transcribe Google Drive videos with Apify.

### Option 1: API Endpoint

```bash
curl -X POST "http://localhost:8000/automation/transcribe-video" \
  -H "Content-Type: application/json" \
  -d '{
    "airtable_record_id": "rec123456",
    "youtube_url": "https://youtu.be/VIDEO_ID"
  }'
```

### Option 2: Python

```python
from src.services.video_transcription_service import VideoTranscriptionService
from src.services.airtable_service import AirtableService

transcription_service = VideoTranscriptionService()
airtable_service = AirtableService()

# Transcribe and update Airtable
transcription = transcription_service.get_or_create_transcription(
    video_record_id="rec123456",
    youtube_url="https://youtu.be/VIDEO_ID"
)
```

---

## 🔍 Testing

### 1. Check Health

```bash
curl http://localhost:8000/automation/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "composio": {"configured": true, "status": "ready"},
    "airtable": {"configured": true, "status": "ready"},
    "blotato": {"configured": true, "status": "ready"},
    "transcription": {"configured": true, "status": "ready"}
  }
}
```

### 2. Test with Sample Video

1. Upload an MP4 file to `media_not_uploaded` folder in Google Drive
2. Call the automation endpoint
3. Check that:
   - File uploaded to Blotato ✅
   - Airtable record created ✅
   - File moved to `media_uploaded` ✅
   - Transcription status set to "Pending" ✅

---

## 📁 Folder IDs Reference

| Folder Name | Folder ID | Purpose |
|-------------|-----------|---------|
| media_not_uploaded | `1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ` | Source folder - videos to process |
| media_uploaded | `1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu` | Destination folder - processed videos |

**Google Drive Links:**
- [media_not_uploaded](https://drive.google.com/drive/folders/1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ)
- [media_uploaded](https://drive.google.com/drive/folders/1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu)

---

## 🔧 Troubleshooting

### "COMPOSIO_API_KEY not found"
- Make sure `.env` file has `COMPOSIO_API_KEY=...`
- Restart your FastAPI server after adding the key

### "Google Drive not connected"
- Run `composio add googledrive --user-id pg-dev-tylerai-blotato`
- Complete the OAuth flow in your browser

### "No files found"
- Check that MP4 files exist in `media_not_uploaded` folder
- Verify folder permissions in Google Drive

### "Upload to Blotato failed"
- Check `BLOTATO_API_KEY` is correct
- Verify file is accessible (not private)

### "Airtable record creation failed"
- Check `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`
- Verify table name is `video-uploads`
- Ensure all required fields exist in Airtable

---

## 🔄 Scheduling (Optional)

### Option 1: Cron Job

```bash
# Run every hour
0 * * * * curl -X POST http://localhost:8000/automation/drive-to-blotato \
  -H "Content-Type: application/json" \
  -d '{"source_folder_id": "1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ", "processed_folder_id": "1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu"}'
```

### Option 2: n8n Workflow

1. Create a Schedule Trigger (every 30 minutes)
2. HTTP Request to your automation endpoint
3. Error handling and notifications

---

## 📝 Next Steps

1. **Set up Composio** - Get API key and connect Google Drive
2. **Test the endpoint** - Process a single video
3. **Monitor Airtable** - Verify records are created correctly
4. **Add transcriptions** - Use separate endpoint for YouTube videos
5. **Schedule automation** - Set up cron or n8n workflow

---

## 🤝 Support

If you encounter issues:
1. Check logs in terminal where FastAPI is running
2. Verify all environment variables are set
3. Test each service independently using health endpoint
4. Check Airtable for error messages in failed records
