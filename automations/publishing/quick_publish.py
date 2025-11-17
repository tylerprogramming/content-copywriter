#!/usr/bin/env python3
"""
Quick Publish - Streamlined publishing automation
Automatically finds latest unpublished video and publishes to specified platform
"""

import argparse

from publish_post import publish_latest_video, find_latest_unpublished_video, list_unpublished_videos
from src.config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Quick publish latest video to social media platform')
    parser.add_argument('--list', action='store_true', help='List unpublished videos only')
    parser.add_argument('--check', action='store_true', help='Check latest video info only (no publishing)')
    parser.add_argument('platform', nargs='?', help='Target platform (tiktok, instagram, facebook, etc.)')
    parser.add_argument('text', nargs='?', help='Post content text')
    
    args = parser.parse_args()
    
    print("⚡ Quick Publish - Latest Video to Social Media")
    print("=" * 50)
    print()
    
    # List mode - just show unpublished videos
    if args.list:
        print("🔍 Unpublished videos:")
        videos = list_unpublished_videos(limit=10)
        if not videos:
            print("   No unpublished videos found")
        else:
            for i, video in enumerate(videos, 1):
                print(f"   {i}. {video['record_id']} - {video['created_at']} - {video['account_context']}")
        return
    
    # Check mode - show latest video info only
    if args.check:
        print("🔍 Latest unpublished video:")
        video = find_latest_unpublished_video()
        if not video:
            print("   No unpublished videos found")
        else:
            print(f"   📹 Record: {video['record_id']}")
            print(f"   📅 Created: {video['created_at']}")
            print(f"   📋 Context: {video['account_context']}")
            print(f"   📤 Media URL: {video['blotato_media_url']}")
        return
    
    # For non-list/check modes, validate required arguments
    if not args.list and not args.check:
        if not args.platform or not args.text:
            print("❌ Platform and text are required for publishing")
            parser.print_help()
            return
        
        # Validate platform
        available_platforms = list(config.PLATFORM_ACCOUNT_IDS.keys())
        if args.platform.lower() not in available_platforms:
            print(f"❌ Platform '{args.platform}' not configured")
            print(f"Available platforms: {', '.join(available_platforms)}")
            return
    
    if not args.list and not args.check:
        print(f"🎯 Platform: {args.platform}")
        print(f"📝 Text: {args.text}")
        print()
    
    # Find and publish latest video
    print("🔍 Finding latest unpublished video...")
    result = publish_latest_video(
        platform=args.platform,
        text=args.text,
        account_context=args.platform
    )
    
    if result["success"]:
        print()
        print("✅ PUBLISHED SUCCESSFULLY!")
        print(f"📋 Post ID: {result['post_submission_id']}")
        if "video_info" in result:
            print(f"📹 Video: {result['video_info']['record_id']}")
        print(f"🎯 Platform: {args.platform}")
    else:
        print()
        print(f"❌ FAILED: {result['error']}")
        if result["error_type"] == "not_found":
            print("💡 Upload a video first with: python upload_media.py")

if __name__ == "__main__":
    main()