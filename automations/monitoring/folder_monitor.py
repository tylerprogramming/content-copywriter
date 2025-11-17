#!/usr/bin/env python3
"""
Google Drive Folder Monitor
Automatically uploads videos from 'media_not_uploaded' folder to Blotato,
then moves them to 'media_uploaded' folder on success.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from src.services.media_service import MediaService
from src.services.airtable_service import AirtableService

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

class GoogleDriveFolderMonitor:
    """Monitor Google Drive folders and process video uploads"""
    
    # Google Drive API scopes needed for folder/file operations
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google API client not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2"
            )
        
        self.service = self._authenticate()
        self.media_service = MediaService()
        self.airtable_service = AirtableService()
        
        # Load folder configuration
        self.config = self._load_configuration()
        self.main_folder_id = self.config['main_folder_id']
        self.not_uploaded_folder_id = self.config['not_uploaded_folder_id']
        self.uploaded_folder_id = self.config['uploaded_folder_id']
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Get absolute paths based on this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_dir = os.path.join(current_dir, '..', 'credentials')
        
        # Token file stores user's access and refresh tokens  
        token_path = os.path.join(credentials_dir, 'token.json')
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials are available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_path = os.path.join(credentials_dir, 'credentials.json')
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json not found at {credentials_path}. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for the next run
            os.makedirs(credentials_dir, exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    def _load_configuration(self):
        """Load folder configuration from config file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(current_dir, '..', 'credentials', 'blotato_config.json')
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(
                f"❌ Configuration file '{config_file}' not found!\n"
                "\n🔧 Run setup first:"
                "\n   python setup_blotato_automation.py"
            )
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Validate required fields
            required_fields = ['main_folder_id', 'not_uploaded_folder_id', 'uploaded_folder_id']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            
            pass
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {str(e)}")
    
    def verify_folders(self):
        """Verify that configured folders exist"""
        pass
        
        try:
            # Check if folders still exist
            folder_ids = [self.main_folder_id, self.not_uploaded_folder_id, self.uploaded_folder_id]
            folder_names = ['main folder', 'media_not_uploaded', 'media_uploaded']
            
            for folder_id, name in zip(folder_ids, folder_names):
                self.service.files().get(fileId=folder_id).execute()
                pass
            
            pass
            
        except Exception as e:
            raise ValueError(
                f"❌ Folder verification failed: {str(e)}\n"
                "\n🔧 Try running setup again:"
                "\n   python setup_blotato_automation.py"
            )
    
    def _list_folders_in_parent(self) -> List[Dict[str, Any]]:
        """List all folders in the parent directory"""
        query = f"'{self.parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])
    
    def _create_folder(self, folder_name: str, parent_id: str) -> str:
        """Create a new folder in Google Drive"""
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    def get_videos_in_not_uploaded_folder(self) -> List[Dict[str, Any]]:
        """Get all video files from the 'media_not_uploaded' folder"""
        if not self.not_uploaded_folder_id:
            self.airtable_service.log_warning("FolderMonitor", "media_not_uploaded folder not found!")
            return []
        
        # Query for video files (common video MIME types)
        video_mimes = [
            'video/mp4', 'video/quicktime', 'video/x-msvideo',
            'video/webm', 'video/x-ms-wmv', 'video/3gpp'
        ]
        mime_query = ' or '.join([f"mimeType='{mime}'" for mime in video_mimes])
        
        query = f"'{self.not_uploaded_folder_id}' in parents and ({mime_query}) and trashed=false"
        
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, size, createdTime, webViewLink)",
            orderBy="createdTime desc"
        ).execute()
        
        videos = results.get('files', [])
        pass
        
        return videos
    
    def move_file_to_uploaded_folder(self, file_id: str, file_name: str) -> bool:
        """Move a file from not_uploaded to uploaded folder"""
        try:
            # Get current file to check its parents
            file_metadata = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file_metadata.get('parents'))
            
            # Move the file by updating its parents
            self.service.files().update(
                fileId=file_id,
                addParents=self.uploaded_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            pass
            return True
            
        except Exception as e:
            self.airtable_service.log_error("FolderMonitor", f"Failed to move file '{file_name}': {str(e)}")
            return False
    
    def create_sharing_url(self, file_id: str) -> str:
        """Create a shareable URL for a Google Drive file"""
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    def process_all_videos(self) -> Dict[str, Any]:
        """Complete monitoring workflow with setup verification"""
        self.airtable_service.log_info("FolderMonitor", "Starting monitoring automation with setup verification")
        
        try:
            # Step 1: Verify setup and folders
            self.airtable_service.log_info("FolderMonitor", "Step 1: Verifying setup and folder configuration")
            self.verify_folders()
            self.airtable_service.log_info("FolderMonitor", "✅ Setup verification passed")
            
            # Step 2: Process videos
            return self.process_videos()
            
        except Exception as e:
            self.airtable_service.log_error("FolderMonitor", f"Monitoring automation failed: {str(e)}")
            return {
                "success": False,
                "processed": 0,
                "uploaded": 0,
                "failed": 0,
                "error": str(e),
                "results": []
            }
    
    def process_videos(self) -> Dict[str, Any]:
        """Process all videos in the not_uploaded folder"""
        self.airtable_service.log_info("FolderMonitor", "Step 2: Processing videos in not_uploaded folder")
        
        videos = self.get_videos_in_not_uploaded_folder()
        
        if not videos:
            self.airtable_service.log_info("FolderMonitor", "No videos to process")
            return {
                "success": True,
                "processed": 0,
                "uploaded": 0,
                "failed": 0,
                "results": []
            }
        
        results = []
        uploaded_count = 0
        failed_count = 0
        
        for video in videos:
            file_id = video['id']
            file_name = video['name']
            file_size = int(video.get('size', 0))
            
            pass
            
            try:
                # Create sharing URL for the video
                sharing_url = self.create_sharing_url(file_id)
                
                # Upload to Blotato via our media service
                upload_result = self.media_service.upload_from_google_drive(
                    sharing_url=sharing_url,
                    social_account="automated_upload"
                )
                
                # Move file to uploaded folder on success
                if self.move_file_to_uploaded_folder(file_id, file_name):
                    uploaded_count += 1
                    
                    result = {
                        "success": True,
                        "file_name": file_name,
                        "file_id": file_id,
                        "blotato_media_url": str(upload_result.media_response.url),
                        "airtable_record_id": upload_result.airtable_record_id,
                        "file_size_mb": round(file_size / (1024*1024), 1)
                    }
                    
                    pass
                else:
                    # Upload succeeded but move failed - still count as partial success
                    result = {
                        "success": False,
                        "file_name": file_name,
                        "error": "Upload succeeded but failed to move file",
                        "blotato_media_url": str(upload_result.media_response.url),
                        "airtable_record_id": upload_result.airtable_record_id
                    }
                    failed_count += 1
                
                results.append(result)
                
            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                
                result = {
                    "success": False,
                    "file_name": file_name,
                    "file_id": file_id,
                    "error": error_msg,
                    "file_size_mb": round(file_size / (1024*1024), 1)
                }
                results.append(result)
                
                self.airtable_service.log_error("FolderMonitor", f"Failed to process {file_name}: {error_msg}")
        
        summary = {
            "success": True,
            "processed": len(videos),
            "uploaded": uploaded_count,
            "failed": failed_count,
            "results": results
        }
        
        self.airtable_service.log_info("FolderMonitor", f"Processing complete: {uploaded_count} uploaded, {failed_count} failed")
        return summary

def main():
    """Main function for folder monitoring"""
    print("📂 Google Drive Folder Monitor")
    print("=" * 50)
    print()
    
    try:
        monitor = GoogleDriveFolderMonitor()
        
        # Process videos with setup verification
        results = monitor.process_all_videos()
        
        print()
        print("=" * 50)
        print("📊 PROCESSING SUMMARY")
        print("=" * 50)
        print(f"📹 Videos processed: {results['processed']}")
        print(f"✅ Successfully uploaded: {results['uploaded']}")
        print(f"❌ Failed: {results['failed']}")
        
        if results['results']:
            print()
            print("📋 Details:")
            for result in results['results']:
                status = "✅" if result['success'] else "❌"
                file_name = result['file_name']
                if result['success']:
                    print(f"   {status} {file_name} → Uploaded & Moved")
                else:
                    print(f"   {status} {file_name} → {result['error']}")
        
    except ImportError as e:
        print("❌ Missing Google API dependencies")
        print("Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
        
    except FileNotFoundError as e:
        print("❌ Google Drive API not configured")
        print(str(e))
        print()
        print("🔧 Setup Instructions:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Google Drive API")
        print("3. Create OAuth2 credentials")
        print("4. Download credentials.json to this directory")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()