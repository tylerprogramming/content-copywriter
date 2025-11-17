#!/usr/bin/env python3
"""
Example: Generating Carousel Posts with Blotato

Demonstrates how to create visual carousel posts (quote slides, tweet cards, etc.)
using the Blotato template system.
"""

import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"
CAROUSEL_ENDPOINT = f"{API_BASE_URL}/carousel/generate"

def example_crewai_carousel():
    """Example: CrewAI educational carousel"""

    payload = {
        "inputs": {
            "theme": "light",
            "handle": "tylerreedai",
            "quotes": [
                "CrewAI lets multiple AI agents work together to finish complex tasks end‑to‑end.",
                "Define three pieces: Agents (who), Tasks (what), Tools (how). The crew coordinates.",
                "Give each agent a role, goal, and short backstory for clearer behavior.",
                "Run agents sequentially (handoffs) or hierarchically (manager + workers).",
                "Plug in OpenAI, Anthropic, or local LLMs—and your own Python tools.",
                "Agents share context, review each other's work, and iterate toward better results.",
                "Start small, log and test, then add agents only when one can't reliably finish."
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

    print("=" * 70)
    print("EXAMPLE: CrewAI Educational Carousel")
    print("=" * 70)
    print()
    print(f"📊 Slides: {len(payload['inputs']['quotes'])}")
    print(f"🎨 Theme: {payload['inputs']['theme']}")
    print(f"📐 Aspect Ratio: {payload['inputs']['aspectRatio']}")
    print()

    try:
        response = requests.post(CAROUSEL_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Carousel Generated Successfully!")
        print()
        print(f"📹 Video URL: {result.get('video_url')}")
        print(f"🆔 Render ID: {result.get('render_id')}")
        print(f"📝 Slides Count: {result.get('slides_count')}")
        print(f"💬 Message: {result.get('message')}")
        print()

        if result.get('blotato_response'):
            print("🔍 Full Blotato Response:")
            print(json.dumps(result['blotato_response'], indent=2))

        return result

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_automation_tips_carousel():
    """Example: Automation tips carousel (shorter)"""

    payload = {
        "inputs": {
            "theme": "dark",
            "handle": "tylerreedai",
            "quotes": [
                "3 AI Automation Mistakes Everyone Makes",
                "❌ Building without error handling → workflows crash randomly",
                "❌ No logging → impossible to debug when things break",
                "❌ Hardcoded values → can't reuse or scale",
                "✅ Add retry logic with exponential backoff",
                "✅ Use structured JSON logging",
                "✅ Move configs to environment variables"
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

    print("=" * 70)
    print("EXAMPLE: Automation Tips Carousel (Dark Theme)")
    print("=" * 70)
    print()
    print(f"📊 Slides: {len(payload['inputs']['quotes'])}")
    print(f"🎨 Theme: {payload['inputs']['theme']}")
    print()

    try:
        response = requests.post(CAROUSEL_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Carousel Generated Successfully!")
        print(f"📹 Video URL: {result.get('video_url')}")
        print(f"💬 {result.get('message')}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def example_draft_carousel():
    """Example: Save as draft for review later"""

    payload = {
        "inputs": {
            "theme": "light",
            "handle": "tylerreedai",
            "quotes": [
                "Coming soon: My new AI course",
                "Learn CrewAI from scratch",
                "Build real automations",
                "Ship to production"
            ],
            "verified": True,
            "authorName": "Tyler Reed",
            "aspectRatio": "1:1",  # Square format
            "profileImage": "https://example.com/profile.jpg"
        },
        "render": True,
        "isDraft": True,  # Save as draft!
        "templateId": "/base/v2/tweet-card/ba413be6-a840-4e60-8fd6-0066d3b427df/v1"
    }

    print("=" * 70)
    print("EXAMPLE: Draft Carousel (Review Later)")
    print("=" * 70)
    print()
    print(f"💾 Mode: Draft (won't publish immediately)")
    print(f"📊 Slides: {len(payload['inputs']['quotes'])}")
    print()

    try:
        response = requests.post(CAROUSEL_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()

        print("✅ Draft Saved!")
        print(f"📹 Video URL: {result.get('video_url')}")
        print(f"🆔 Render ID: {result.get('render_id')}")
        print()
        print("💡 Tip: Review in Blotato dashboard before publishing")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print()
    print("🎨 CAROUSEL GENERATION EXAMPLES")
    print()
    print("Make sure the API server is running:")
    print("  uvicorn main:app --reload")
    print()

    input("Press Enter to run Example 1 (CrewAI carousel)...")
    example_crewai_carousel()
    print()

    input("Press Enter to run Example 2 (Automation tips)...")
    example_automation_tips_carousel()
    print()

    input("Press Enter to run Example 3 (Draft mode)...")
    example_draft_carousel()
    print()

    print("=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print()
    print("🎯 Next Steps:")
    print("   • Check your Blotato dashboard for generated carousels")
    print("   • Download videos for publishing")
    print("   • Customize templates in Blotato")
    print()


if __name__ == "__main__":
    main()
