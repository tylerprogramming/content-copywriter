#!/usr/bin/env python3
"""
Example: Upload Media from URLs (including Google Drive)

Demonstrates how to upload media from various URLs, with automatic
Google Drive link conversion.
"""

import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/media/upload-from-url"


def example_google_drive_upload():
    """Example: Upload from Google Drive share link"""

    # Google Drive share link (will be auto-converted to direct download)
    payload = {
        "url": "https://drive.google.com/file/d/1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq/view?usp=drive_link"
    }

    print("=" * 70)
    print("EXAMPLE 1: Upload from Google Drive Share Link")
    print("=" * 70)
    print()
    print(f"📁 Original URL: {payload['url']}")
    print()

    try:
        response = requests.post(UPLOAD_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Upload Successful!")
        print()
        print(f"🔗 Media URL (Blotato): {result.get('media_url')}")
        print(f"📋 Original URL: {result.get('original_url')}")

        if result.get('converted_url'):
            print(f"🔄 Converted URL: {result.get('converted_url')}")

        print(f"💬 Message: {result.get('message')}")
        print()

        return result

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_direct_url_upload():
    """Example: Upload from direct image URL"""

    payload = {
        "url": "https://images.unsplash.com/photo-1518770660439-4636190af475"
    }

    print("=" * 70)
    print("EXAMPLE 2: Upload from Direct Image URL")
    print("=" * 70)
    print()
    print(f"🌐 URL: {payload['url']}")
    print()

    try:
        response = requests.post(UPLOAD_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Upload Successful!")
        print()
        print(f"🔗 Media URL: {result.get('media_url')}")
        print(f"💬 Message: {result.get('message')}")
        print()

        # Note: converted_url will be None for non-Google Drive URLs
        if result.get('converted_url'):
            print(f"🔄 URL was converted (Google Drive)")
        else:
            print("ℹ️  No conversion needed (already direct URL)")
        print()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_use_in_post():
    """Example: Upload media then use in a post"""

    print("=" * 70)
    print("EXAMPLE 3: Upload Media + Publish Post")
    print("=" * 70)
    print()

    # Step 1: Upload media from URL
    upload_payload = {
        "url": "https://drive.google.com/file/d/1FV22cjjlR-kZWinOz24gfNdBnNpaGJeq/view?usp=drive_link"
    }

    print("📤 Step 1: Uploading media from Google Drive...")
    print()

    try:
        upload_response = requests.post(UPLOAD_ENDPOINT, json=upload_payload)
        upload_response.raise_for_status()
        upload_result = upload_response.json()

        media_url = upload_result.get('media_url')
        print(f"✅ Media uploaded: {media_url}")
        print()

        # Step 2: Use media URL in a post
        post_payload = {
            "platform": "linkedin",
            "text": "Check out this amazing automation workflow! 🤖",
            "media_url": media_url
        }

        print("📝 Step 2: Publishing post with uploaded media...")
        print()

        post_response = requests.post(
            f"{API_BASE_URL}/posts/media",
            json=post_payload
        )
        post_response.raise_for_status()
        post_result = post_response.json()

        print("✅ Post Published Successfully!")
        print()
        print(f"🆔 Submission ID: {post_result.get('submission_id')}")
        print(f"📱 Platform: {post_result.get('platform')}")
        print(f"💬 Message: {post_result.get('message')}")
        print()

        return {
            "upload": upload_result,
            "post": post_result
        }

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print()
    print("🎨 MEDIA UPLOAD FROM URL EXAMPLES")
    print()
    print("Make sure the API server is running:")
    print("  uvicorn main:app --reload")
    print()

    input("Press Enter to run Example 1 (Google Drive upload)...")
    example_google_drive_upload()
    print()

    input("Press Enter to run Example 2 (Direct URL upload)...")
    example_direct_url_upload()
    print()

    input("Press Enter to run Example 3 (Upload + Post)...")
    example_use_in_post()
    print()

    print("=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print()
    print("🎯 Key Features:")
    print("   • Automatic Google Drive link conversion")
    print("   • Support for direct media URLs")
    print("   • Returns both original and converted URLs")
    print("   • Media URLs ready for use in posts")
    print()


if __name__ == "__main__":
    main()
