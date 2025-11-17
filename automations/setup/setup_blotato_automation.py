#!/usr/bin/env python3
"""
Blotato Automation Setup Service
One-time setup that creates Google Drive folder structure and saves configuration
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BlotatoSetupService:
    """One-time setup service for Blotato automation"""
    
    # Google Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    # Configuration
    MAIN_FOLDER_NAME = "Blotato Content Management"
    NOT_UPLOADED_FOLDER_NAME = "media_not_uploaded"
    UPLOADED_FOLDER_NAME = "media_uploaded"
    CONFIG_FILE = "credentials/blotato_config.json"
    
    def __init__(self):
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google API client not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2"
            )
        
        self.service = None
        self.config = {}
    
    def authenticate_google_drive(self):
        """Authenticate with Google Drive API"""
        logger.info("🔐 Authenticating with Google Drive API...")
        
        creds = None
        
        # Check for existing token
        token_path = 'credentials/token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired token...")
                creds.refresh(Request())
            else:
                credentials_path = 'credentials/credentials.json'
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"❌ credentials.json not found at {credentials_path}!\n"
                        "\n🔧 Setup Instructions:"
                        "\n1. Go to Google Cloud Console (https://console.cloud.google.com/)"
                        "\n2. Create/select a project"
                        "\n3. Enable Google Drive API"
                        "\n4. Create OAuth 2.0 credentials (Desktop Application)"
                        "\n5. Download and rename to 'credentials.json'"
                        "\n6. Place in automations/credentials/ folder"
                    )
                
                logger.info("🌐 Opening browser for Google authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future runs
            os.makedirs('credentials', exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info("💾 Saved authentication token")
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Google Drive API authenticated successfully!")
    
    def check_existing_setup(self) -> bool:
        """Check if setup already exists"""
        if os.path.exists(self.CONFIG_FILE):
            logger.info(f"📋 Found existing config: {self.CONFIG_FILE}")
            
            with open(self.CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
            
            # Need to authenticate before we can verify folders
            self.authenticate_google_drive()
            
            # Verify folders still exist
            if self.verify_folder_structure():
                logger.info("✅ Existing folder structure is valid")
                return True
            else:
                logger.warning("⚠️  Existing folders not found, will recreate")
                return False
        
        return False
    
    def verify_folder_structure(self) -> bool:
        """Verify that configured folders still exist in Google Drive"""
        try:
            folder_ids = [
                self.config.get('main_folder_id'),
                self.config.get('not_uploaded_folder_id'), 
                self.config.get('uploaded_folder_id')
            ]
            
            for folder_id in folder_ids:
                if not folder_id:
                    return False
                
                # Check if folder exists
                try:
                    self.service.files().get(fileId=folder_id).execute()
                except:
                    logger.warning(f"❌ Folder {folder_id} not found")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying folders: {str(e)}")
            return False
    
    def create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """Create a folder in Google Drive"""
        logger.info(f"📁 Creating folder: {folder_name}")
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        logger.info(f"✅ Created folder '{folder_name}': {folder_id}")
        return folder_id
    
    def create_folder_structure(self):
        """Create the complete Blotato folder structure"""
        logger.info("🏗️  Creating Blotato folder structure...")
        
        # Create main folder
        main_folder_id = self.create_folder(self.MAIN_FOLDER_NAME)
        
        # Create subfolders
        not_uploaded_folder_id = self.create_folder(
            self.NOT_UPLOADED_FOLDER_NAME, 
            main_folder_id
        )
        
        uploaded_folder_id = self.create_folder(
            self.UPLOADED_FOLDER_NAME,
            main_folder_id
        )
        
        # Save configuration
        self.config = {
            "main_folder_id": main_folder_id,
            "main_folder_name": self.MAIN_FOLDER_NAME,
            "not_uploaded_folder_id": not_uploaded_folder_id,
            "not_uploaded_folder_name": self.NOT_UPLOADED_FOLDER_NAME,
            "uploaded_folder_id": uploaded_folder_id,
            "uploaded_folder_name": self.UPLOADED_FOLDER_NAME,
            "created_date": datetime.now().isoformat(),
            "setup_version": "1.0"
        }
        
        logger.info("🎯 Folder structure created successfully!")
    
    def save_configuration(self):
        """Save configuration to file"""
        logger.info(f"💾 Saving configuration to {self.CONFIG_FILE}...")
        
        # Ensure credentials directory exists
        os.makedirs('credentials', exist_ok=True)
        
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info("✅ Configuration saved!")
    
    def create_shareable_links(self) -> Dict[str, str]:
        """Create shareable links for the folders"""
        logger.info("🔗 Creating shareable links...")
        
        links = {}
        
        folders = {
            "main_folder": self.config['main_folder_id'],
            "not_uploaded_folder": self.config['not_uploaded_folder_id'],
            "uploaded_folder": self.config['uploaded_folder_id']
        }
        
        for name, folder_id in folders.items():
            # Make folder shareable (anyone with link can view)
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            try:
                self.service.permissions().create(
                    fileId=folder_id,
                    body=permission
                ).execute()
                
                # Get shareable link
                folder_info = self.service.files().get(
                    fileId=folder_id, 
                    fields='webViewLink'
                ).execute()
                
                links[name] = folder_info['webViewLink']
                logger.info(f"🔗 {name}: {folder_info['webViewLink']}")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not create shareable link for {name}: {str(e)}")
        
        return links
    
    def display_setup_summary(self, links: Dict[str, str]):
        """Display setup completion summary"""
        print("\n" + "=" * 60)
        print("🎉 BLOTATO AUTOMATION SETUP COMPLETED!")
        print("=" * 60)
        print()
        print("📁 Google Drive Folder Structure Created:")
        print(f"   📂 {self.config['main_folder_name']}/")
        print(f"      ├── {self.config['not_uploaded_folder_name']}/")
        print(f"      └── {self.config['uploaded_folder_name']}/")
        print()
        
        if links:
            print("🔗 Shareable Links:")
            if 'main_folder' in links:
                print(f"   📂 Main Folder: {links['main_folder']}")
            if 'not_uploaded_folder' in links:
                print(f"   📥 Drop Videos Here: {links['not_uploaded_folder']}")
            if 'uploaded_folder' in links:
                print(f"   ✅ Processed Videos: {links['uploaded_folder']}")
            print()
        
        print("💾 Configuration:")
        print(f"   📄 Config File: {self.CONFIG_FILE}")
        print(f"   🔑 Token File: token.json")
        print()
        
        print("🚀 Next Steps:")
        print("   1. Add video files to the 'media_not_uploaded' folder")
        print("   2. Run the automation service:")
        print("      python automation_service.py")
        print("   3. Videos will be processed at 8AM and 8PM daily")
        print()
        
        print("🧪 Test Commands:")
        print("   python automation_service.py --test     # Test setup")
        print("   python automation_service.py --run-now  # Process videos now")
    
    def run_setup(self):
        """Run the complete setup process"""
        try:
            logger.info("🚀 Starting Blotato Automation Setup...")
            
            # Step 1: Check existing setup
            if self.check_existing_setup():
                print("✅ Setup already completed!")
                links = self.create_shareable_links()
                self.display_setup_summary(links)
                return
            
            # Step 2: Authenticate (if not already done)
            if not self.service:
                self.authenticate_google_drive()
            
            # Step 3: Create folder structure
            self.create_folder_structure()
            
            # Step 4: Save configuration
            self.save_configuration()
            
            # Step 5: Create shareable links
            links = self.create_shareable_links()
            
            # Step 6: Display summary
            self.display_setup_summary(links)
            
            logger.info("🎉 Setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
            raise

def main():
    """Main setup function"""
    print("🔧 Blotato Automation Setup")
    print("=" * 50)
    print()
    
    try:
        setup_service = BlotatoSetupService()
        setup_service.run_setup()
        
    except ImportError as e:
        print("❌ Missing Google API dependencies:")
        print("   pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
        
    except FileNotFoundError as e:
        print(str(e))
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())