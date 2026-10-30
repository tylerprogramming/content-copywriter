# Skool Post Generation API Guide

## Overview

The Skool API generates day-specific community posts automatically. Each day of the week has a different post type optimized for engagement.

## Quick Start

### Simple Usage (Auto-detect day)
```bash
POST /skool/post/generate
{
  "topic": "3 things every AI Agent should have",
  "content_details": "1) Error handling 2) Logging 3) State management"
}
```

## Request Structure

### Required
- **topic** (string): Title or headline of your post

### Optional (but recommended!)
- **content_details** (string): The full story, details, or main points
- **day** (string): Override auto-detection (`monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `weekend`)
- **inputs** (object): Day-specific data (member names, platforms, etc.)
- **additional_context** (string): Tone, style, or requirements

## How to Use Each Field

### `topic`
**What it is:** The title/headline/main subject
**Example:** `"3 things every AI Agent should have"`

### `content_details`
**What it is:** Your raw material - the full story, details, or points
**When to use:** Almost always! This is where you put the actual content
**Example:** `"1) Error handling with retries - catches API failures. 2) Structured logging - makes debugging easier. 3) State persistence - resume workflows."`

### `additional_context`
**What it is:** How you want it written
**Examples:**
- `"Make it beginner-friendly"`
- `"Keep it vulnerable and honest"`
- `"Focus on actionable takeaways"`

---

## Day Types & Examples

### Monday - Value-Driven Post
**Goal:** Teach something actionable

```json
{
  "topic": "3 things every AI Agent should have",
  "content_details": "1) Error handling with exponential backoff - catches API failures and retries intelligently. 2) Structured logging using JSON format - makes debugging 10x easier. 3) State persistence with Redis - tracks progress across runs.",
  "additional_context": "Make it beginner-friendly with code examples"
}
```

### Tuesday - Offer Post
**Goal:** Showcase paid community value

```json
{
  "topic": "How Sarah automated her lead generation",
  "day": "tuesday",
  "content_details": "Sarah was spending 2 hours daily entering leads manually. Now she has a CrewAI workflow that scrapes 5 sources, deduplicates, enriches data, and adds to Airtable automatically. Saved 10+ hours per week.",
  "inputs": {
    "member_name": "Sarah",
    "paid_group_name": "AI Automations Community"
  }
}
```

### Wednesday - Personal Story
**Goal:** Build trust through vulnerability

```json
{
  "topic": "When I over-engineered my automation",
  "day": "wednesday",
  "content_details": "I spent 2 weeks building a custom state manager for my AI agents. Created a whole PostgreSQL system. Then I read the CrewAI Flows docs and realized it's built-in. Wasted 80 hours reinventing the wheel. Now I always check docs first.",
  "additional_context": "Make it vulnerable and relatable"
}
```

### Thursday - Cross-Platform Share
**Goal:** Repurpose content from other platforms

```json
{
  "topic": "How I built an AI Workout Planner",
  "day": "thursday",
  "content_details": "Just posted a full tutorial on YouTube about chaining multiple AI tools together. Shows how to use CrewAI Flows + Composio to build a workout planner that adapts to your goals.",
  "inputs": {
    "platform": "YouTube",
    "link": "https://youtube.com/watch?v=...",
    "question": "Who's built something similar?"
  }
}
```

### Friday - Community Wins
**Goal:** Celebrate members and create momentum

```json
{
  "topic": "Community wins this week",
  "day": "friday",
  "content_details": "Alex connected Airtable to CrewAI for automatic lead generation. He went from 2 hours of manual entry daily to zero. The workflow scrapes 5 sources, deduplicates, enriches, and syncs to Airtable.",
  "inputs": {
    "member_name": "Alex",
    "achievement": "automated lead generation"
  }
}
```

### Weekend - Off-Topic
**Goal:** Lighthearted connection

```json
{
  "topic": "If AI could automate one part of your life outside work, what would it be?",
  "day": "weekend"
}
```

---

## Common Patterns

### Pattern 1: Just topic (minimal)
```json
{
  "topic": "Quick debugging tip for AI agents"
}
```
✅ Works, but AI has less to work with

### Pattern 2: Topic + Details (recommended)
```json
{
  "topic": "3 debugging tips",
  "content_details": "1) Add structured logging 2) Use retry logic 3) Track state"
}
```
✅ **Best practice** - Clear structure with raw material

### Pattern 3: Full context (maximum)
```json
{
  "topic": "Why your automations break",
  "content_details": "Most failures come from lack of error handling...",
  "additional_context": "Make it beginner-friendly",
  "inputs": {
    "example_framework": "CrewAI"
  }
}
```
✅ Most control over output

---

## Tips

### ✅ DO:
- Use `content_details` for the meat of your post
- Be specific with your details
- Use `additional_context` for tone/style
- Let the AI shape your raw content into engaging posts

### ❌ DON'T:
- Put everything in `topic` (it's just the title!)
- Skip `content_details` for complex posts
- Expect the AI to invent facts
- Forget to provide your actual story/details

---

## Response Format

```json
{
  "success": true,
  "day": "monday",
  "post_type": "Value-Driven Post",
  "content": "Generated post content...",
  "character_count": 450,
  "word_count": 87,
  "model_used": "gpt-5.6-sol",
  "message": "Value-Driven Post generated successfully",
  "generated_at": "2025-01-06T12:00:00"
}
```

---

## Testing

Run the test script to see examples:
```bash
python test_skool_generation.py
```

Or start the server and visit the docs:
```bash
uvicorn main:app --reload
# Visit: http://localhost:8000/docs
# Find: POST /skool/post/generate
```

---

## Need Help?

- **Auto-detect day:** Just send `topic` (and optionally `content_details`)
- **Specific day:** Add `"day": "monday"` (or tuesday, etc.)
- **More control:** Use `additional_context` for tone/style requirements
- **Day-specific data:** Use `inputs` for member names, platforms, etc.
