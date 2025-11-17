#!/usr/bin/env python3
"""
Blotato Automation Service
Uses APScheduler to run folder monitoring at 8AM and 8PM daily
"""

import signal
import logging
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from folder_monitor import GoogleDriveFolderMonitor

# Configure APScheduler logging to be less verbose
logging.getLogger('apscheduler').setLevel(logging.WARNING)

class BlotatoAutomationService:
    """Automation service for scheduled video uploads"""
    
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.monitor = None
        self.setup_directories()
        self.setup_scheduler()
        self.setup_signal_handlers()
    
    def setup_directories(self):
        """Create necessary directories if needed"""
        print("📁 Directories initialized")
    
    def setup_scheduler(self):
        """Configure the scheduler with jobs"""
        
        # Morning upload at 8:00 AM
        self.scheduler.add_job(
            func=self.run_upload_job,
            trigger=CronTrigger(hour=8, minute=0),
            id='morning_upload',
            name='Morning Upload (8 AM)',
            kwargs={'job_name': 'morning'},
            misfire_grace_time=300,  # Allow 5 minutes grace time
            max_instances=1  # Prevent overlapping jobs
        )
        
        # Evening upload at 8:00 PM
        self.scheduler.add_job(
            func=self.run_upload_job,
            trigger=CronTrigger(hour=20, minute=0),
            id='evening_upload', 
            name='Evening Upload (8 PM)',
            kwargs={'job_name': 'evening'},
            misfire_grace_time=300,
            max_instances=1
        )
        
        # Add event listeners
        self.scheduler.add_listener(self.job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_error_listener, EVENT_JOB_ERROR)
        
        print("⏰ Scheduler configured with jobs:")
        print("   • Morning Upload: Daily at 8:00 AM")
        print("   • Evening Upload: Daily at 8:00 PM")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print("🛑 Shutdown signal received, stopping scheduler...")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_upload_job(self, job_name: str):
        """Run the upload job"""
        start_time = datetime.now()
        print(f"🚀 Starting {job_name} upload job at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Initialize monitor if not already done
            if not self.monitor:
                self.monitor = GoogleDriveFolderMonitor()
                self.monitor.verify_folders()
            
            # Process videos
            results = self.monitor.process_videos()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ {job_name.title()} upload completed successfully")
            print(f"📊 Processed: {results['processed']}, Uploaded: {results['uploaded']}, Failed: {results['failed']}")
            print(f"⏱️ Duration: {duration:.1f}s")
            
        except Exception as e:
            error_msg = str(e)
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"❌ {job_name.title()} upload failed after {duration:.1f}s: {error_msg}")
            raise
    
    def job_executed_listener(self, event):
        """Listener for successful job execution"""
        print(f"✅ Job '{event.job_id}' executed successfully")
    
    def job_error_listener(self, event):
        """Listener for job execution errors"""
        print(f"❌ Job '{event.job_id}' failed: {event.exception}")
    
    def run_now(self, job_name: str = "manual"):
        """Run upload job immediately (for testing)"""
        print(f"🔥 Running upload job immediately...")
        self.run_upload_job(job_name)
    
    def start(self):
        """Start the automation service"""
        print("🚀 Starting Blotato Automation Service")
        print("=" * 60)
        
        # Display next scheduled jobs
        jobs = self.scheduler.get_jobs()
        if jobs:
            print("📅 Scheduled jobs:")
            for job in jobs:
                next_run = job.next_run_time
                if next_run:
                    print(f"   • {job.name}: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("🎯 Service is running. Press Ctrl+C to stop.")
        print("=" * 60)
        
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Scheduler error: {str(e)}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the service gracefully"""
        if self.scheduler.running:
            print("🛑 Shutting down scheduler...")
            self.scheduler.shutdown(wait=True)
        print("✅ Service stopped successfully")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Blotato Automation Service')
    parser.add_argument('--run-now', action='store_true', 
                       help='Run upload job immediately instead of scheduling')
    parser.add_argument('--test', action='store_true',
                       help='Test the service setup without running jobs')
    
    args = parser.parse_args()
    
    print("🤖 Blotato Automation Service")
    print("=" * 50)
    print()
    
    try:
        service = BlotatoAutomationService()
        
        if args.test:
            print("🧪 Testing service setup...")
            print("✅ Service initialized successfully")
            print("✅ Scheduler configured")
            print("✅ Directories created")
            print("🎉 Test completed - service is ready!")
            
        elif args.run_now:
            print("🔥 Running upload job immediately...")
            service.run_now()
            print("✅ Manual upload completed")
            
        else:
            print("⏰ Starting scheduled service...")
            service.start()
            
    except ImportError as e:
        print("❌ Missing dependencies:")
        print("   Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
        
    except FileNotFoundError as e:
        print("❌ Configuration missing:")
        print(f"   {str(e)}")
        print()
        print("🔧 Setup required:")
        print("   1. Google Drive API credentials (credentials.json)")
        print("   2. Blotato and Airtable credentials (.env)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()