#!/usr/bin/env python3
"""
Example: Multi-Platform Carousel Publishing

Demonstrates how to publish carousel posts to multiple platforms simultaneously
with a single API call.
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://localhost:8000"
MULTI_PUBLISH_ENDPOINT = f"{API_BASE_URL}/carousel/publish-multi"


def example_all_platforms_immediate():
    """Example: Publish to all platforms immediately"""

    payload = {
        "platforms": ["instagram", "linkedin", "tiktok"],
        "account_ids": {
            "instagram": "28",
            "linkedin": "45",
            "tiktok": "199"
        },
        "text": "CrewAI 7-step quickstart in tweet cards. Cover slide or quote-only? #CrewAI #AIagents",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e088e690-2712-4b5f-a8f0-b90427c33839.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e907f942-68b1-497d-bf33-6f64f80458b5.jpg"
        ]
    }

    print("=" * 70)
    print("EXAMPLE 1: Publish to All Platforms (Immediate)")
    print("=" * 70)
    print()
    print(f"📱 Platforms: {', '.join(payload['platforms'])}")
    print(f"📊 Media Count: {len(payload['media_urls'])}")
    print(f"📝 Caption: {payload['text'][:50]}...")
    print()

    try:
        response = requests.post(MULTI_PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print(f"✅ Multi-Platform Publish Complete!")
        print()
        print(f"📊 Total Platforms: {result.get('total_platforms')}")
        print(f"✅ Successful: {result.get('successful_platforms')}")
        print(f"❌ Failed: {result.get('failed_platforms')}")
        print()

        print("📋 Individual Results:")
        for platform_result in result.get('results', []):
            platform = platform_result.get('platform')
            success = platform_result.get('success')
            submission_id = platform_result.get('post_submission_id')

            if success:
                print(f"  ✅ {platform.upper()}: {submission_id}")
            else:
                error = platform_result.get('error', 'Unknown error')
                print(f"  ❌ {platform.upper()}: {error}")

        print()
        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_scheduled_multi_platform():
    """Example: Schedule to multiple platforms"""

    # Schedule for 3 hours from now
    scheduled_time = (datetime.utcnow() + timedelta(hours=3)).isoformat() + "Z"

    payload = {
        "platforms": ["instagram", "linkedin", "tiktok"],
        "account_ids": {
            "instagram": "28",
            "linkedin": "45",
            "tiktok": "199"
        },
        "text": "AI Automation tips you can't miss! 🚀 #AI #Automation",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg"
        ],
        "scheduled_time": scheduled_time,
        "tiktok_title": "AI Automation Tips"
    }

    print("=" * 70)
    print("EXAMPLE 2: Scheduled Multi-Platform Publish")
    print("=" * 70)
    print()
    print(f"📱 Platforms: {', '.join(payload['platforms'])}")
    print(f"⏰ Scheduled For: {scheduled_time}")
    print(f"🎬 TikTok Title: {payload['tiktok_title']}")
    print()

    try:
        response = requests.post(MULTI_PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print(f"✅ Scheduled Successfully!")
        print()
        print(f"📊 Total Platforms: {result.get('total_platforms')}")
        print(f"✅ Successful: {result.get('successful_platforms')}")
        print()

        print("📋 Scheduled Posts:")
        for platform_result in result.get('results', []):
            if platform_result.get('success'):
                platform = platform_result.get('platform')
                submission_id = platform_result.get('post_submission_id')
                print(f"  📅 {platform.upper()}: {submission_id}")

        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_selective_platforms():
    """Example: Publish to only 2 platforms (Instagram + LinkedIn)"""

    payload = {
        "platforms": ["instagram", "linkedin"],
        "account_ids": {
            "instagram": "28",
            "linkedin": "45"
        },
        "text": "Professional carousel content for Instagram and LinkedIn 📊",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e088e690-2712-4b5f-a8f0-b90427c33839.jpg"
        ]
    }

    print("=" * 70)
    print("EXAMPLE 3: Selective Platforms (Instagram + LinkedIn)")
    print("=" * 70)
    print()
    print(f"📱 Platforms: {', '.join(payload['platforms'])}")
    print(f"ℹ️  Only publishing to Instagram and LinkedIn")
    print()

    try:
        response = requests.post(MULTI_PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print(f"✅ Published Successfully!")
        print()
        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_full_workflow_multi_platform():
    """Example: Generate carousel, then publish to all platforms"""

    print("=" * 70)
    print("EXAMPLE 4: Complete Workflow (Generate → Publish to All)")
    print("=" * 70)
    print()

    # Step 1: Generate carousel
    print("📊 Step 1: Generating carousel...")
    carousel_payload = {
        "inputs": {
            "theme": "dark",
            "handle": "tylerreedai",
            "quotes": [
                "3 AI Automation Mistakes",
                "❌ No error handling",
                "❌ No logging",
                "❌ Hardcoded values",
                "✅ Add retry logic",
                "✅ Use structured logging",
                "✅ Use environment variables"
            ],
            "verified": True,
            "authorName": "Tyler Reed",
            "aspectRatio": "4:5",
            "profileImage": "https://example.com/profile.jpg"
        },
        "render": True,
        "isDraft": False,
        "templateId": "/base/v2/tweet-card/ba413be6-a840-4e60-8fd6-0066d3b427df/v1"
    }

    try:
        carousel_response = requests.post(
            f"{API_BASE_URL}/carousel/generate",
            json=carousel_payload
        )
        carousel_response.raise_for_status()
        carousel_result = carousel_response.json()

        render_id = carousel_result.get("render_id")
        print(f"✅ Carousel generated! Render ID: {render_id}")
        print()

        # Step 2: Poll for completion
        print("⏳ Step 2: Waiting for video completion...")
        import time

        for attempt in range(30):
            video_response = requests.get(f"{API_BASE_URL}/carousel/video/{render_id}")
            video_response.raise_for_status()
            video_result = video_response.json()

            status = video_result.get("status")
            print(f"   Attempt {attempt + 1}: {status}")

            if status == "completed":
                media_url = video_result.get("media_url")
                print(f"✅ Video ready!")
                print()

                # Step 3: Publish to all platforms
                print("📱 Step 3: Publishing to all platforms...")
                multi_publish_payload = {
                    "platforms": ["instagram", "linkedin", "tiktok"],
                    "account_ids": {
                        "instagram": "28",
                        "linkedin": "45",
                        "tiktok": "199"
                    },
                    "text": "3 AI Automation Mistakes Everyone Makes (and how to fix them) 🤖 #AI #Automation",
                    "media_urls": [media_url],
                    "tiktok_title": "AI Automation Mistakes"
                }

                publish_response = requests.post(MULTI_PUBLISH_ENDPOINT, json=multi_publish_payload)
                publish_response.raise_for_status()
                publish_result = publish_response.json()

                print(f"✅ Published to {publish_result.get('successful_platforms')}/{publish_result.get('total_platforms')} platforms!")
                print()

                print("📋 Platform Results:")
                for platform_result in publish_result.get('results', []):
                    platform = platform_result.get('platform')
                    success = platform_result.get('success')
                    submission_id = platform_result.get('post_submission_id')

                    if success:
                        print(f"  ✅ {platform.upper()}: {submission_id}")

                print()

                return {
                    "carousel": carousel_result,
                    "video": video_result,
                    "publish": publish_result
                }

            elif status == "failed":
                print("❌ Video generation failed")
                return None

            time.sleep(2)

        print("❌ Timeout waiting for video")
        return None

    except Exception as e:
        print(f"❌ Error in workflow: {e}")


def main():
    """Run all examples"""
    print()
    print("🌐 MULTI-PLATFORM CAROUSEL PUBLISHING EXAMPLES")
    print()
    print("Make sure the API server is running:")
    print("  uvicorn main:app --reload")
    print()
    print("⚠️  Update account_id values in the script with your actual Blotato account IDs:")
    print("   • Instagram: account_ids['instagram']")
    print("   • LinkedIn: account_ids['linkedin']")
    print("   • TikTok: account_ids['tiktok']")
    print()

    input("Press Enter to run Example 1 (All platforms immediate)...")
    example_all_platforms_immediate()
    print()

    input("Press Enter to run Example 2 (Scheduled multi-platform)...")
    example_scheduled_multi_platform()
    print()

    input("Press Enter to run Example 3 (Selective platforms)...")
    example_selective_platforms()
    print()

    input("Press Enter to run Example 4 (Full workflow)...")
    example_full_workflow_multi_platform()
    print()

    print("=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print()
    print("🎯 Key Features:")
    print("   • Publish to multiple platforms with one request")
    print("   • Automatic payload transformation per platform")
    print("   • Schedule posts across all platforms simultaneously")
    print("   • Individual success/failure tracking per platform")
    print("   • TikTok-specific options (title, privacy, etc.)")
    print("   • Selective platform publishing")
    print()


if __name__ == "__main__":
    main()
