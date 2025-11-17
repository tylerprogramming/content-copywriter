# Quick Start - Google Drive to Blotato Automation

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
pip install composio-core composio-openai openai
```

### 2. Add to `.env`
```bash
COMPOSIO_API_KEY=your_key_here
```

### 3. Connect Google Drive
```bash
composio add googledrive --user-id pg-dev-tylerai-blotato
```

### 4. Start Server
```bash
uvicorn main:app --reload
```

### 5. Process Videos
```bash
curl -X POST "http://localhost:8000/automation/drive-to-blotato" \
  -H "Content-Type: application/json" \
  -d '{
    "source_folder_id": "1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ",
    "processed_folder_id": "1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu"
  }'
```

---

## 📋 What This Does

For each MP4 in `media_not_uploaded` folder:
1. ✅ Upload to Blotato
2. ✅ Create Airtable record with upload info
3. ✅ Move to `media_uploaded` folder
4. ✅ Set transcription status to "Pending"

---

## 🔗 API Endpoints

### Process Drive Folder
**POST** `/automation/drive-to-blotato`

```json
{
  "source_folder_id": "1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ",
  "processed_folder_id": "1aGqd9_TowK3xtU1u84bevqgKiDVmaDIu"
}
```

### Transcribe Video
**POST** `/automation/transcribe-video`

```json
{
  "airtable_record_id": "rec123456",
  "youtube_url": "https://youtu.be/VIDEO_ID"
}
```

### Health Check
**GET** `/automation/health`

---

## 📊 View Results

- **API Docs**: http://localhost:8000/docs
- **Airtable**: Check `video-uploads` table
- **Blotato**: Check uploaded media URLs in response

---

## 🐛 Troubleshooting

**No files found?**
- Put MP4 files in [media_not_uploaded](https://drive.google.com/drive/folders/1mpBqg18Otd-UnmgAL_FlAWa8cS51ONYJ)

**Composio error?**
- Run: `composio add googledrive --user-id pg-dev-tylerai-blotato`

**Upload failed?**
- Check `.env` has all keys set

---

## 📖 Full Documentation

See [AUTOMATION_SETUP.md](./AUTOMATION_SETUP.md) for complete setup guide.
