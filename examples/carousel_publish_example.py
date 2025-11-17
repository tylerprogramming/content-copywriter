#!/usr/bin/env python3
"""
Example: Publish Carousel Posts to Social Media

Demonstrates how to publish carousel posts (generated from templates or uploaded media)
to various social media platforms with scheduling options.
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://localhost:8000"
PUBLISH_ENDPOINT = f"{API_BASE_URL}/carousel/publish"


def example_instagram_immediate():
    """Example: Publish carousel to Instagram immediately"""

    payload = {
        "platform": "instagram",
        "account_id": "28",  # Your Instagram account ID
        "text": "CrewAI 7-step quickstart in tweet cards. Cover slide or quote-only? #CrewAI #AIagents",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e088e690-2712-4b5f-a8f0-b90427c33839.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e907f942-68b1-497d-bf33-6f64f80458b5.jpg"
        ]
    }

    print("=" * 70)
    print("EXAMPLE 1: Instagram Carousel (Immediate)")
    print("=" * 70)
    print()
    print(f"📱 Platform: {payload['platform']}")
    print(f"📊 Media Count: {len(payload['media_urls'])}")
    print(f"📝 Caption: {payload['text'][:50]}...")
    print()

    try:
        response = requests.post(PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Post Published Successfully!")
        print()
        print(f"🆔 Submission ID: {result.get('post_submission_id')}")
        print(f"📱 Platform: {result.get('platform')}")
        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_instagram_scheduled():
    """Example: Schedule Instagram carousel for later"""

    # Schedule for 2 hours from now
    scheduled_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"

    payload = {
        "platform": "instagram",
        "account_id": "28",
        "text": "Scheduled carousel post - AI automation tips! 🤖",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg"
        ],
        "scheduled_time": scheduled_time
    }

    print("=" * 70)
    print("EXAMPLE 2: Instagram Carousel (Scheduled)")
    print("=" * 70)
    print()
    print(f"📱 Platform: {payload['platform']}")
    print(f"⏰ Scheduled For: {scheduled_time}")
    print()

    try:
        response = requests.post(PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Post Scheduled Successfully!")
        print()
        print(f"🆔 Submission ID: {result.get('post_submission_id')}")
        print(f"⏰ Scheduled Time: {result.get('scheduled_time')}")
        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_tiktok_with_options():
    """Example: Publish to TikTok with platform-specific options"""

    payload = {
        "platform": "tiktok",
        "account_id": "199",  # Your TikTok account ID
        "text": "CrewAI 7-step quickstart in tweet cards. Cover slide or quote-only? #CrewAI #AIagents",
        "media_urls": [
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-52603780-0f9e-4b64-98cc-72b6f41b259d.jpg",
            "https://database.blotato.io/storage/v1/object/public/public_media/d2b8d644-0e81-4573-a71a-e52410f6fe62/videogen2-render-e088e690-2712-4b5f-a8f0-b90427c33839.jpg"
        ],
        # TikTok-specific options
        "tiktok_title": "CrewAI: 7-step quickstart",
        "tiktok_privacy_level": "PUBLIC_TO_EVERYONE",
        "tiktok_auto_add_music": True,
        "tiktok_is_draft": False
    }

    print("=" * 70)
    print("EXAMPLE 3: TikTok Carousel with Options")
    print("=" * 70)
    print()
    print(f"📱 Platform: {payload['platform']}")
    print(f"📊 Media Count: {len(payload['media_urls'])}")
    print(f"🎵 Auto Add Music: {payload['tiktok_auto_add_music']}")
    print(f"🔒 Privacy: {payload['tiktok_privacy_level']}")
    print()

    try:
        response = requests.post(PUBLISH_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ TikTok Post Published Successfully!")
        print()
        print(f"🆔 Submission ID: {result.get('post_submission_id')}")
        print(f"📱 Platform: {result.get('platform')}")
        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_full_workflow():
    """Example: Complete workflow - Generate carousel, poll for completion, then publish"""

    print("=" * 70)
    print("EXAMPLE 4: Full Workflow (Generate → Poll → Publish)")
    print("=" * 70)
    print()

    # Step 1: Generate carousel
    print("📊 Step 1: Generating carousel...")
    carousel_payload = {
        "inputs": {
            "theme": "light",
            "handle": "tylerreedai",
            "quotes": [
                "AI Automation Made Simple",
                "Build once, run forever",
                "Scale without limits"
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

        # Step 2: Poll for video completion
        print("⏳ Step 2: Waiting for video to complete...")
        import time

        max_attempts = 30  # 1 minute max (2 sec intervals)
        for attempt in range(max_attempts):
            video_response = requests.get(f"{API_BASE_URL}/carousel/video/{render_id}")
            video_response.raise_for_status()
            video_result = video_response.json()

            status = video_result.get("status")
            print(f"   Attempt {attempt + 1}: Status = {status}")

            if status == "completed":
                media_url = video_result.get("media_url")
                print(f"✅ Video ready! URL: {media_url}")
                print()

                # Step 3: Publish to Instagram
                print("📱 Step 3: Publishing to Instagram...")
                publish_payload = {
                    "platform": "instagram",
                    "account_id": "28",
                    "text": "AI Automation tips you need to know! 🚀 #AI #Automation",
                    "media_urls": [media_url]
                }

                publish_response = requests.post(PUBLISH_ENDPOINT, json=publish_payload)
                publish_response.raise_for_status()
                publish_result = publish_response.json()

                print("✅ Published to Instagram!")
                print()
                print(f"🆔 Submission ID: {publish_result.get('post_submission_id')}")
                print(f"💬 Message: {publish_result.get('message')}")
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

        print("❌ Timeout waiting for video completion")
        return None

    except Exception as e:
        print(f"❌ Error in workflow: {e}")


def main():
    """Run all examples"""
    print()
    print("🎨 CAROUSEL PUBLISHING EXAMPLES")
    print()
    print("Make sure the API server is running:")
    print("  uvicorn main:app --reload")
    print()
    print("⚠️  Update account_id values with your actual Blotato account IDs")
    print()

    input("Press Enter to run Example 1 (Instagram immediate)...")
    example_instagram_immediate()
    print()

    input("Press Enter to run Example 2 (Instagram scheduled)...")
    example_instagram_scheduled()
    print()

    input("Press Enter to run Example 3 (TikTok with options)...")
    example_tiktok_with_options()
    print()

    input("Press Enter to run Example 4 (Full workflow)...")
    example_full_workflow()
    print()

    print("=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print()
    print("🎯 Key Features:")
    print("   • Publish to Instagram, TikTok, LinkedIn, Twitter, Facebook")
    print("   • Schedule posts for later")
    print("   • Platform-specific options (TikTok privacy, music, etc.)")
    print("   • Support for multiple media URLs")
    print("   • Complete workflow from generation to publishing")
    print()


if __name__ == "__main__":
    main()
