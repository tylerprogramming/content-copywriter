#!/usr/bin/env python3
"""
Social Media Scheduling Automation

Automatically finds the latest video from Airtable video-uploads table and schedules it 
for publishing to platforms not yet in the Social Account column.
Schedules for next day at 3 PM and updates Social Account after successful publication.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.services.airtable_service import AirtableService, VideoPublicationRecord
from src.services.content_generation_service import ContentGenerationService
from src.services.video_transcription_service import VideoTranscriptionService
from src.blotato.client import BlotatoClient
from src.blotato.models import PostRequest, Post, PostContent, TikTokTarget, YouTubeTarget, GenericTarget, PlatformType
from src.config import config

class SocialMediaScheduler:
    """Handles automated scheduling of videos across social media platforms"""
    
    def __init__(self, schedule_posts: bool = False, test_mode: bool = False):
        self.airtable = AirtableService()
        self.content_generator = ContentGenerationService()
        self.transcription_service = VideoTranscriptionService()
        self.blotato_client = BlotatoClient()
        self.available_platforms = list(config.PLATFORM_ACCOUNT_IDS.keys())
        self.schedule_posts = schedule_posts
        self.test_mode = test_mode
        
        # Log which platforms are configured for debugging
        self.airtable.log_info("ScheduleAutomation", f"Configured platforms: {self.available_platforms}")
        self.airtable.log_info("ScheduleAutomation", f"Scheduling mode: {'Scheduled' if schedule_posts else 'Immediate'}")
        self.airtable.log_info("ScheduleAutomation", f"Test mode: {'ENABLED - No actual publishing' if test_mode else 'DISABLED - Will publish'}")
    
    def get_latest_video_for_publishing(self) -> Optional[Dict]:
        """Get the most recent video that needs publishing to available platforms"""
        try:
            # Get latest successful upload from video-uploads table
            uploads_table = self.airtable.api.table(self.airtable.base_id, self.airtable.media_uploads_table)
            
            # Get successful uploads sorted by created date (newest first)
            upload_records = uploads_table.all(
                sort=["-Created At"],
                formula="{Upload Status} = 'Success'"
            )
            
            if not upload_records:
                return None
            
            # Check the latest record
            latest_record = upload_records[0]
            record_data = {
                "record_id": latest_record["id"],
                "google_drive_url": latest_record["fields"].get("Google Drive URL"),
                "google_drive_file_id": latest_record["fields"].get("Google Drive File ID"),
                "blotato_media_url": latest_record["fields"].get("Blotato Media URL"),
                "created_at": latest_record["fields"].get("Created At")
            }
            
            # Verify it has blotato media URL
            if not record_data["blotato_media_url"]:
                return None
            
            # Get already published platforms by checking video-publications table directly
            published_platforms = self.get_published_platforms_for_video(record_data["record_id"])
            
            # Find platforms that need publishing (available but not yet published)
            pending_platforms = []
            for platform in self.available_platforms:
                is_published = platform.lower() in [p.lower() for p in published_platforms]
                self.airtable.log_info("ScheduleAutomation", f"Platform {platform}: Published={is_published}")
                
                if not is_published:
                    pending_platforms.append(platform)
                    self.airtable.log_info("ScheduleAutomation", f"Added {platform} to pending list")
            
            record_data["published_platforms"] = published_platforms
            record_data["pending_platforms"] = pending_platforms
            
            # Debug logging to see what's happening
            self.airtable.log_info("ScheduleAutomation", f"Video {record_data['record_id']}:")
            self.airtable.log_info("ScheduleAutomation", f"  Published platforms (from video-publications): {published_platforms}")
            self.airtable.log_info("ScheduleAutomation", f"  Available platforms: {self.available_platforms}")
            self.airtable.log_info("ScheduleAutomation", f"  Pending platforms: {pending_platforms}")
            
            # CRITICAL: Print to console for immediate debugging
            print(f"\n🔍 DEBUG PLATFORM LOGIC:")
            print(f"Video ID: {record_data['record_id']}")
            print(f"Published platforms: {published_platforms}")
            print(f"Available platforms: {self.available_platforms}")
            print(f"Pending platforms: {pending_platforms}")
            print(f"Should publish to: {pending_platforms}")
            print()
            
            if not pending_platforms:
                self.airtable.log_info("ScheduleAutomation", "No pending platforms - video already published to all available platforms")
                return None
            
            return record_data
            
        except Exception as e:
            self.airtable.log_error("ScheduleAutomation", f"Failed to get latest video: {str(e)}")
            return None
    
    def get_published_platforms_for_video(self, video_record_id: str) -> List[str]:
        """Get list of platforms already published for a specific video"""
        try:
            publications_table = self.airtable.api.table(self.airtable.base_id, self.airtable.video_publications_table)
            
            # Get all records and manually filter since linked records are stored as lists
            all_records = publications_table.all()
            self.airtable.log_info("ScheduleAutomation", f"Checking {len(all_records)} publication records")
            
            published_platforms = []
            matching_records = 0
            
            for record in all_records:
                video_upload_record = record["fields"].get("Video Upload Record")
                platform = record["fields"].get("Platform")
                publication_status = record["fields"].get("Publication Status")
                
                # Check if this record is linked to our target video
                # Video Upload Record is a list of linked record IDs
                is_match = False
                if isinstance(video_upload_record, list):
                    if video_record_id in video_upload_record:
                        is_match = True
                elif video_upload_record == video_record_id:
                    is_match = True
                
                if is_match:
                    matching_records += 1
                    self.airtable.log_info("ScheduleAutomation", f"Found publication: Platform={platform}, Status={publication_status}")
                    
                    # Only count successful or scheduled publications
                    if platform and publication_status in ["Success", "Scheduled"]:
                        published_platforms.append(platform.lower())
            
            self.airtable.log_info("ScheduleAutomation", f"Found {matching_records} total publication records for video {video_record_id}")
            
            # Remove duplicates and return
            unique_platforms = list(set(published_platforms))
            self.airtable.log_info("ScheduleAutomation", f"Unique published platforms: {unique_platforms}")
            
            return unique_platforms
            
        except Exception as e:
            self.airtable.log_error("ScheduleAutomation", f"Failed to get published platforms for video {video_record_id}: {str(e)}")
            return []
    
    def get_next_day_3pm(self) -> datetime:
        """Calculate next day at 3 PM for scheduling"""
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        return scheduled_time
    
    def generate_platform_content(self, video_record: Dict, platform: str) -> Dict:
        """Generate AI-powered content for specific platform"""
        try:
            # Get or create video transcription
            transcription = self.transcription_service.get_or_create_transcription(
                video_record["record_id"],
                video_record.get("google_drive_file_id", "")
            )
            
            # Fallback video context
            video_context = f"Video content from {video_record.get('created_at', 'recent upload')}"
            
            # Generate platform-specific content using AI with transcription
            content = self.content_generator.generate_post_content(
                platform=platform,
                video_context=video_context,
                video_transcription=transcription,  # This will make content much better!
                brand_voice="professional yet engaging",
                target_audience="business professionals and entrepreneurs"
            )
            
            return {
                "title": content.title,
                "text": content.text,
                "hashtags": content.hashtags,
                "character_count": content.character_count
            }
            
        except Exception as e:
            self.airtable.log_error("ContentGeneration", f"Failed for {platform}: {str(e)}")
            
            # Return fallback content
            return {
                "title": f"New Content on {platform.title()}!",
                "text": f"Check out our latest content! 🚀 #{platform} #content #video",
                "hashtags": [f"#{platform}", "#content", "#video"],
                "character_count": 50
            }
    
    def schedule_post_to_platform(self, video_record: Dict, platform: str, scheduled_time: datetime) -> bool:
        """Schedule a single post to a specific platform"""
        try:
            # Get platform account ID
            account_id = config.PLATFORM_ACCOUNT_IDS.get(platform)
            if not account_id:
                error_msg = f"No account ID configured for platform: {platform}"
                self.airtable.log_error("ScheduleAutomation", error_msg)
                return False
            
            if self.test_mode:
                print(f"🧪 TEST MODE: Would publish to {platform} but skipping content generation and API call")
                return True
            
            # Generate platform-specific content
            content_data = self.generate_platform_content(video_record, platform)
            
            print(f"\n📝 {platform.upper()} CONTENT GENERATED:")
            print(f"Title: {content_data['title']}")
            print(f"Text: {content_data['text'][:200]}...")
            print(f"Character Count: {content_data['character_count']}")
            
            # Build post content
            post_content = PostContent(
                text=content_data["text"],
                mediaUrls=[video_record["blotato_media_url"]],
                platform=PlatformType(platform.lower())
            )
            
            # Build platform-specific target
            if platform == "tiktok":
                target = TikTokTarget(**config.PLATFORM_SETTINGS["tiktok"])
            elif platform == "youtube":
                # YouTube requires a title
                youtube_settings = config.PLATFORM_SETTINGS["youtube"].copy()
                youtube_settings["title"] = content_data["title"]
                target = YouTubeTarget(**youtube_settings)
            else:
                # Generic target for other platforms (Instagram, LinkedIn, etc.)
                platform_enum = PlatformType(platform.lower())
                target = GenericTarget(targetType=platform_enum)
            
            # Create post request
            post = Post(
                accountId=account_id,
                content=post_content,
                target=target
            )
            
            # Create post request with optional scheduling
            if self.schedule_posts:
                post_request = PostRequest(
                    post=post,
                    scheduledTime=scheduled_time
                )
            else:
                # Publish immediately
                post_request = PostRequest(post=post)
            
            # Submit to Blotato API
            response = self.blotato_client.publish_post(post_request)
            
            # Create video publication record
            publication_status = "Scheduled" if self.schedule_posts else "Success"
            publication_record = VideoPublicationRecord(
                video_upload_record=video_record["record_id"],
                platform=platform,
                post_submission_id=response.postSubmissionId,
                post_text=content_data["text"],
                publication_status=publication_status,
                scheduled_date=scheduled_time if self.schedule_posts else None
            )
            
            self.airtable.create_video_publication_record(publication_record)
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to schedule {platform} post: {str(e)}"
            self.airtable.log_error("ScheduleAutomation", error_msg, stack_trace=str(e))
            return False
    
    def update_social_account_column(self, video_record: Dict, new_platforms: List[str]) -> bool:
        """Social Account is now a computed field - no longer needs manual updates"""
        # Since Social Account is computed from video-publications table,
        # we don't need to update it manually anymore
        self.airtable.log_info("ScheduleAutomation", f"Social Account will auto-update via computed field for platforms: {new_platforms}")
        return True
    
    def schedule_video_to_platforms(self, video_record: Dict) -> Dict:
        """Schedule video to all pending platforms"""
        scheduled_time = self.get_next_day_3pm()
        results = {
            "video_id": video_record["record_id"],
            "scheduled_time": scheduled_time,
            "successes": [],
            "failures": [],
            "total_platforms": len(video_record["pending_platforms"])
        }
        
        for platform in video_record["pending_platforms"]:
            
            success = self.schedule_post_to_platform(video_record, platform, scheduled_time)
            
            if success:
                results["successes"].append(platform)
            else:
                results["failures"].append(platform)
        
        # Update Social Account column with successful publications
        if results["successes"]:
            self.update_social_account_column(video_record, results["successes"])
        
        # Log overall results
        success_count = len(results["successes"])
        failure_count = len(results["failures"])
        
        self.airtable.log_info("ScheduleAutomation", f"Scheduling complete: {success_count} successes, {failure_count} failures")
        
        return results
    
    def run_automation(self) -> Dict:
        """Main automation workflow"""
        self.airtable.log_info("ScheduleAutomation", "Starting automation")
        
        try:
            # Get latest video that needs publishing
            video_record = self.get_latest_video_for_publishing()
            
            if not video_record:
                message = "No videos need publishing (either no videos found or already published to all platforms)"
                self.airtable.log_info("ScheduleAutomation", message)
                return {
                    "success": True,
                    "message": message,
                    "action_required": None
                }
            
            # Schedule to all pending platforms
            results = self.schedule_video_to_platforms(video_record)
            
            if results["successes"]:
                message = f"Scheduled video to {len(results['successes'])} platforms"
                self.airtable.log_info("ScheduleAutomation", message)
                return {
                    "success": True,
                    "message": message,
                    "video_id": results["video_id"],
                    "scheduled_time": results["scheduled_time"],
                    "platforms": results["successes"],
                    "failures": results["failures"]
                }
            else:
                message = "Failed to schedule to any platforms"
                self.airtable.log_error("ScheduleAutomation", message)
                return {
                    "success": False,
                    "message": message,
                    "video_id": results["video_id"],
                    "failures": results["failures"]
                }
                
        except Exception as e:
            error_msg = f"Automation failed: {str(e)}"
            self.airtable.log_error("ScheduleAutomation", error_msg, stack_trace=str(e))
            return {
                "success": False,
                "message": error_msg,
                "error": str(e)
            }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media Publishing Automation')
    parser.add_argument('--schedule', action='store_true', 
                       help='Schedule posts for next day at 3 PM (default: publish immediately)')
    args = parser.parse_args()
    
    mode = "Scheduled" if args.schedule else "Immediate"
    print(f"🤖 Social Media Publishing Automation - {mode} Mode")
    print("=" * 50)
    
    try:
        scheduler = SocialMediaScheduler(schedule_posts=args.schedule, test_mode=False)
        result = scheduler.run_automation()
        
        print(f"\n📋 Results:")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        
        if result.get("video_id"):
            print(f"Video ID: {result['video_id']}")
        
        if result.get("scheduled_time"):
            print(f"Scheduled Time: {result['scheduled_time']}")
        
        if result.get("platforms"):
            print(f"Platforms: {', '.join(result['platforms'])}")
        
        if result.get("failures"):
            print(f"Failures: {', '.join(result['failures'])}")
        
        if result.get("action_required"):
            print(f"\n💡 Action Required: {result['action_required']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()