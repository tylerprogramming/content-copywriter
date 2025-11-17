#!/usr/bin/env python3
"""
Video Transcription Automation

Focused solely on transcribing videos that are missing transcriptions.
Finds videos in video-uploads table and processes them using Whisper AI.
Can run once manually or continuously with APScheduler every hour.
"""

from datetime import datetime
from typing import List, Dict, Optional

from src.services.airtable_service import AirtableService
from src.services.video_transcription_service import VideoTranscriptionService

class TranscriptionAutomation:
    """Handles automated transcription of uploaded videos"""
    
    def __init__(self):
        self.airtable = AirtableService()
        self.transcription_service = VideoTranscriptionService()
    
    def find_videos_needing_transcription(self) -> List[Dict]:
        """Find videos that need transcription"""
        try:
            uploads_table = self.airtable.api.table(self.airtable.base_id, self.airtable.media_uploads_table)
            
            # Get successful uploads that don't have transcription yet
            records = uploads_table.all(
                formula="AND({Upload Status} = 'Success', OR({Transcription Status} = '', {Transcription Status} = 'Failed', {Transcription} = ''))",
                sort=["-Created At"]
            )
            
            videos_needing_transcription = []
            for record in records:
                video_info = {
                    "record_id": record["id"],
                    "google_drive_file_id": record["fields"].get("Google Drive File ID"),
                    "google_drive_url": record["fields"].get("Google Drive URL"),
                    "created_at": record["fields"].get("Created At"),
                    "transcription_status": record["fields"].get("Transcription Status", ""),
                    "blotato_media_url": record["fields"].get("Blotato Media URL")
                }
                
                # Only include if we have the Google Drive file ID
                if video_info["google_drive_file_id"]:
                    videos_needing_transcription.append(video_info)
            
            self.airtable.log_info("TranscriptionAutomation", f"Found {len(videos_needing_transcription)} videos needing transcription")
            return videos_needing_transcription
            
        except Exception as e:
            error_msg = f"Failed to find videos needing transcription: {str(e)}"
            self.airtable.log_error("TranscriptionAutomation", error_msg, stack_trace=str(e))
            return []
    
    def process_video_transcriptions(self, video_list: List[Dict]) -> Dict:
        """Process transcriptions for a list of videos"""
        results = {
            "total_videos": len(video_list),
            "successful_transcriptions": 0,
            "failed_transcriptions": 0,
            "skipped": 0,
            "details": []
        }
        
        for video in video_list:
            record_id = video["record_id"]
            file_id = video["google_drive_file_id"]
            
            self.airtable.log_info("TranscriptionAutomation", f"Processing transcription for video: {record_id}")
            
            try:
                # Attempt transcription
                transcription = self.transcription_service.get_or_create_transcription(record_id, file_id)
                
                if transcription:
                    results["successful_transcriptions"] += 1
                    results["details"].append({
                        "record_id": record_id,
                        "status": "success",
                        "transcription_length": len(transcription)
                    })
                else:
                    results["failed_transcriptions"] += 1
                    results["details"].append({
                        "record_id": record_id,
                        "status": "failed",
                        "error": "Transcription returned empty"
                    })
                    
            except Exception as e:
                results["failed_transcriptions"] += 1
                error_msg = f"Transcription failed for {record_id}: {str(e)}"
                self.airtable.log_error("TranscriptionAutomation", error_msg, stack_trace=str(e))
                results["details"].append({
                    "record_id": record_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def run_transcription_batch(self) -> Dict:
        """Run a batch of transcriptions"""
        self.airtable.log_info("TranscriptionAutomation", "Starting transcription batch")
        
        try:
            # Find videos needing transcription
            videos_to_process = self.find_videos_needing_transcription()
            
            if not videos_to_process:
                self.airtable.log_info("TranscriptionAutomation", "No videos need transcription")
                return {
                    "success": True,
                    "message": "No videos need transcription",
                    "results": {
                        "total_videos": 0,
                        "successful_transcriptions": 0,
                        "failed_transcriptions": 0,
                        "skipped": 0,
                        "details": []
                    }
                }
            
            # Process transcriptions
            results = self.process_video_transcriptions(videos_to_process)
            
            # Log summary
            summary_msg = f"Transcription batch complete: {results['successful_transcriptions']} success, {results['failed_transcriptions']} failed"
            self.airtable.log_info("TranscriptionAutomation", summary_msg)
            
            return {
                "success": True,
                "message": summary_msg,
                "results": results
            }
            
        except Exception as e:
            error_msg = f"Transcription batch failed: {str(e)}"
            self.airtable.log_error("TranscriptionAutomation", error_msg, stack_trace=str(e))
            return {
                "success": False,
                "message": error_msg,
                "error": str(e)
            }

def main():
    """CLI entry point for manual execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Video Transcription Automation')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously with hourly checks (default: run once)')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check transcription service dependencies')
    args = parser.parse_args()
    
    print("🎤 Video Transcription Automation")
    print("=" * 50)
    
    try:
        automation = TranscriptionAutomation()
        
        if args.check_deps:
            # Check dependencies
            deps = automation.transcription_service.check_dependencies()
            print("📋 Dependencies Status:")
            for dep, available in deps.items():
                status = "✅" if available else "❌"
                print(f"  {status} {dep}")
            
            if not all(deps.values()):
                print("\n❌ Missing dependencies!")
                print("Run: python setup_transcription.py")
                return
            else:
                print("\n✅ All dependencies available!")
                
        elif args.continuous:
            # Run with scheduler
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.cron import CronTrigger
            
            scheduler = BlockingScheduler()
            
            def scheduled_transcription():
                print(f"\n⏰ Running scheduled transcription check at {datetime.now()}")
                result = automation.run_transcription_batch()
                print(f"📊 Result: {result['message']}")
                if result.get('results'):
                    r = result['results']
                    print(f"   Videos processed: {r['total_videos']}")
                    print(f"   Successful: {r['successful_transcriptions']}")
                    print(f"   Failed: {r['failed_transcriptions']}")
            
            # Schedule to run every hour
            scheduler.add_job(
                scheduled_transcription,
                CronTrigger(minute=0),  # Run at the top of every hour
                id='transcription_hourly'
            )
            
            print("🕐 Starting continuous transcription automation (hourly checks)")
            print("Press Ctrl+C to stop")
            print()
            
            # Run once immediately
            scheduled_transcription()
            
            # Start scheduler
            scheduler.start()
            
        else:
            # Run once
            print("🚀 Running transcription batch...")
            result = automation.run_transcription_batch()
            
            print(f"\n📋 Results:")
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            if result.get('results'):
                r = result['results']
                print(f"\n📊 Details:")
                print(f"Total videos: {r['total_videos']}")
                print(f"Successful transcriptions: {r['successful_transcriptions']}")
                print(f"Failed transcriptions: {r['failed_transcriptions']}")
                
                if r['details']:
                    print(f"\n📝 Individual results:")
                    for detail in r['details'][:5]:  # Show first 5
                        status_emoji = "✅" if detail['status'] == 'success' else "❌"
                        print(f"  {status_emoji} {detail['record_id']}: {detail['status']}")
                        if detail['status'] == 'success' and 'transcription_length' in detail:
                            print(f"      Transcription: {detail['transcription_length']} characters")
                    
                    if len(r['details']) > 5:
                        print(f"  ... and {len(r['details']) - 5} more")
            
            if not result['success']:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()