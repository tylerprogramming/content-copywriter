#!/usr/bin/env python3
"""
Daily Pipeline Orchestrator

Orchestrates the 3 main automations:
1. Monitoring with Setup Verification (automations/monitoring/folder_monitor.py)
2. Video Transcription (automations/transcription/transcription_automation.py) 
3. Smart Publishing (automations/publishing/schedule_automation.py)

This is just the orchestrator - setup verification happens in monitoring automation.
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

from src.services.airtable_service import AirtableService

class DailyAutomation:
    """Orchestrates the complete daily content automation pipeline"""
    
    def __init__(self):
        self.airtable = AirtableService()
        self.session_id = f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.airtable.log_info("DailyAutomation", f"Daily automation session started: {self.session_id}")
    
    def run_folder_monitoring(self) -> Dict[str, Any]:
        """Step 1: Monitor Google Drive folders and upload new videos"""
        try:
            self.airtable.log_info("DailyAutomation", "Step 1: Running folder monitoring")
            
            # Import and run folder monitor
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitoring'))
            from folder_monitor import GoogleDriveFolderMonitor
            
            monitor = GoogleDriveFolderMonitor()
            result = monitor.process_all_videos()
            
            self.airtable.log_info("DailyAutomation", f"Folder monitoring complete: {result['uploaded']} uploaded, {result['failed']} failed")
            
            return {
                "success": True,
                "step": "folder_monitoring",
                "uploaded_count": result['uploaded'],
                "failed_count": result['failed'],
                "message": f"Processed {result['processed']} videos"
            }
            
        except Exception as e:
            error_msg = f"Folder monitoring failed: {str(e)}"
            self.airtable.log_error("DailyAutomation", error_msg, stack_trace=str(e))
            return {
                "success": False,
                "step": "folder_monitoring",
                "error": str(e),
                "message": error_msg
            }
    
    def run_transcription_batch(self) -> Dict[str, Any]:
        """Step 2: Transcribe any videos missing transcriptions"""
        try:
            self.airtable.log_info("DailyAutomation", "Step 2: Running transcription batch")
            
            # Import transcription automation
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcription'))
            from transcription_automation import TranscriptionAutomation
            
            transcription = TranscriptionAutomation()
            result = transcription.run_transcription_batch()
            
            if result['success'] and result.get('results'):
                r = result['results']
                self.airtable.log_info("DailyAutomation", f"Transcription batch complete: {r['successful_transcriptions']} success, {r['failed_transcriptions']} failed")
            
            return {
                "success": result['success'],
                "step": "transcription",
                "message": result['message'],
                "transcription_results": result.get('results')
            }
            
        except Exception as e:
            error_msg = f"Transcription batch failed: {str(e)}"
            self.airtable.log_error("DailyAutomation", error_msg, stack_trace=str(e))
            return {
                "success": False,
                "step": "transcription",
                "error": str(e),
                "message": error_msg
            }
    
    def run_publishing(self, schedule_posts: bool = False) -> Dict[str, Any]:
        """Step 3: Publish or schedule posts for latest videos"""
        try:
            mode = "scheduled" if schedule_posts else "immediate"
            self.airtable.log_info("DailyAutomation", f"Step 3: Running publishing ({mode} mode)")
            
            # Import and run publishing automation
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'publishing'))
            from schedule_automation import SocialMediaScheduler
            
            scheduler = SocialMediaScheduler(schedule_posts=schedule_posts)
            result = scheduler.run_automation()
            
            self.airtable.log_info("DailyAutomation", f"Publishing complete: {result['message']}")
            
            return {
                "success": result['success'],
                "step": "publishing",
                "message": result['message'],
                "publishing_results": {
                    "video_id": result.get('video_id'),
                    "platforms": result.get('platforms', []),
                    "failures": result.get('failures', []),
                    "scheduled_time": result.get('scheduled_time')
                }
            }
            
        except Exception as e:
            error_msg = f"Publishing failed: {str(e)}"
            self.airtable.log_error("DailyAutomation", error_msg, stack_trace=str(e))
            return {
                "success": False,
                "step": "publishing",
                "error": str(e),
                "message": error_msg
            }
    
    def run_complete_pipeline(self, schedule_posts: bool = False) -> Dict[str, Any]:
        """Run the complete daily automation pipeline"""
        pipeline_start = datetime.now()
        self.airtable.log_info("DailyAutomation", "Starting complete daily automation pipeline")
        
        results = {
            "session_id": self.session_id,
            "start_time": pipeline_start,
            "steps": {},
            "overall_success": True,
            "summary": {}
        }
        
        # Step 1: Folder Monitoring
        print("📁 Step 1: Monitoring Google Drive folders...")
        folder_result = self.run_folder_monitoring()
        results["steps"]["folder_monitoring"] = folder_result
        
        if not folder_result["success"]:
            results["overall_success"] = False
        
        # Wait a moment between steps
        time.sleep(2)
        
        # Step 2: Transcription
        print("\n🎤 Step 2: Processing video transcriptions...")
        transcription_result = self.run_transcription_batch()
        results["steps"]["transcription"] = transcription_result
        
        if not transcription_result["success"]:
            results["overall_success"] = False
        
        # Wait a moment between steps
        time.sleep(2)
        
        # Step 3: Publishing
        mode = "scheduled" if schedule_posts else "immediate"
        print(f"\n📤 Step 3: Publishing content ({mode} mode)...")
        publishing_result = self.run_publishing(schedule_posts)
        results["steps"]["publishing"] = publishing_result
        
        if not publishing_result["success"]:
            results["overall_success"] = False
        
        # Compile summary
        end_time = datetime.now()
        duration = (end_time - pipeline_start).total_seconds()
        
        results["end_time"] = end_time
        results["duration_seconds"] = duration
        results["summary"] = {
            "videos_uploaded": folder_result.get("uploaded_count", 0),
            "videos_transcribed": transcription_result.get("transcription_results", {}).get("successful_transcriptions", 0),
            "platforms_published": len(publishing_result.get("publishing_results", {}).get("platforms", [])),
            "total_duration": f"{duration:.1f} seconds"
        }
        
        # Log final summary
        summary_msg = f"Daily automation complete: {results['summary']['videos_uploaded']} uploaded, {results['summary']['videos_transcribed']} transcribed, {results['summary']['platforms_published']} platforms published"
        self.airtable.log_info("DailyAutomation", summary_msg)
        
        return results

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Content Automation Pipeline')
    parser.add_argument('--step', choices=['folder', 'transcription', 'publishing', 'all'], 
                       default='all', help='Run specific step or complete pipeline')
    parser.add_argument('--schedule', action='store_true',
                       help='Schedule posts for next day (only for publishing step)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously with daily schedule')
    args = parser.parse_args()
    
    print("🤖 Daily Content Automation Pipeline")
    print("=" * 50)
    
    try:
        automation = DailyAutomation()
        
        if args.continuous:
            # Run with individual automation schedules
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.cron import CronTrigger
            
            scheduler = BlockingScheduler()
            
            def monitoring_job():
                print(f"\n📁 Running monitoring job at {datetime.now()}")
                result = automation.run_folder_monitoring()
                print(f"📊 Monitoring: {result['message']}")
                if result.get('uploaded_count', 0) > 0:
                    print(f"   Uploaded: {result['uploaded_count']} videos")
            
            def transcription_job():
                print(f"\n🎤 Running transcription job at {datetime.now()}")
                result = automation.run_transcription_batch()
                print(f"📊 Transcription: {result['message']}")
                if result.get('transcription_results'):
                    r = result['transcription_results']
                    if r['successful_transcriptions'] > 0:
                        print(f"   Transcribed: {r['successful_transcriptions']} videos")
            
            def publishing_job():
                print(f"\n📤 Running publishing job at {datetime.now()}")
                result = automation.run_publishing(schedule_posts=args.schedule)
                print(f"📊 Publishing: {result['message']}")
                if result.get('publishing_results', {}).get('platforms'):
                    platforms = result['publishing_results']['platforms']
                    print(f"   Published to: {', '.join(platforms)}")
            
            # Schedule monitoring: 8 AM and 8 PM daily
            scheduler.add_job(
                monitoring_job,
                CronTrigger(hour=8, minute=0),
                id='monitoring_morning'
            )
            scheduler.add_job(
                monitoring_job,
                CronTrigger(hour=20, minute=0),
                id='monitoring_evening'
            )
            
            # Schedule transcription: Every hour
            scheduler.add_job(
                transcription_job,
                CronTrigger(minute=0),  # Every hour at minute 0
                id='transcription_hourly'
            )
            
            # Schedule publishing: Daily at 3 PM
            scheduler.add_job(
                publishing_job,
                CronTrigger(hour=15, minute=0),
                id='publishing_daily'
            )
            
            print("📅 Starting comprehensive automation service:")
            print("   • Monitoring: 8 AM and 8 PM daily")
            print("   • Transcription: Every hour")
            print("   • Publishing: 3 PM daily")
            print("Press Ctrl+C to stop")
            print()
            
            # Run each job once immediately
            print("🚀 Running initial jobs...")
            monitoring_job()
            time.sleep(2)
            transcription_job() 
            time.sleep(2)
            publishing_job()
            
            # Start scheduler
            scheduler.start()
            
        elif args.step == 'all':
            # Run complete pipeline once
            result = automation.run_complete_pipeline(schedule_posts=args.schedule)
            
            print(f"\n📋 Pipeline Results:")
            print(f"Overall Success: {result['overall_success']}")
            print(f"Duration: {result['summary']['total_duration']}")
            print()
            print(f"📊 Summary:")
            print(f"• Videos uploaded: {result['summary']['videos_uploaded']}")
            print(f"• Videos transcribed: {result['summary']['videos_transcribed']}")
            print(f"• Platforms published: {result['summary']['platforms_published']}")
            print()
            
            # Show step details
            for step_name, step_result in result['steps'].items():
                status = "✅" if step_result['success'] else "❌"
                print(f"{status} {step_name.title()}: {step_result['message']}")
            
        else:
            # Run individual step
            if args.step == 'folder':
                result = automation.run_folder_monitoring()
            elif args.step == 'transcription':
                result = automation.run_transcription_batch()
            elif args.step == 'publishing':
                result = automation.run_publishing(schedule_posts=args.schedule)
            
            print(f"\n📋 {args.step.title()} Results:")
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            if not result['success']:
                print(f"Error: {result.get('error', 'Unknown error')}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()