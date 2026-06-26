# System Architecture
# Playplate AI Social Media Manager

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAYPLATE AI SMM ARCHITECTURE                     │
│                   Dr. Anshu Gupta — Chandigarh Dentist               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                               │
│                                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ OpenAI  │  │ Claude  │  │ Google  │  │  Meta   │  │LinkedIn │  │
│  │ GPT-4o  │  │3.5 Son. │  │ Gemini  │  │  Graph  │  │  API    │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │
│       │             │            │             │             │       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │  Kling  │  │ Runway  │  │  Pika   │  │DALL-E 3 │  │YouTube  │  │
│  │  Video  │  │  Video  │  │  Video  │  │ Images  │  │  API    │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    Cloudflare     │
                    │   CDN + WAF + DNS │
                    └─────────┬─────────┘
                              │ HTTPS
                    ┌─────────▼─────────┐
                    │   Nginx (SSL)     │
                    │  Reverse Proxy    │
                    └────┬──────┬───────┘
                         │      │
         ┌───────────────▼──┐  ┌▼──────────────────┐
         │ React Frontend   │  │   FastAPI Backend  │
         │ (social.playplate│  │   (Port 8000)      │
         │  .in/client)     │  │   /api/*           │
         │  /admin          │  │                    │
         └──────────────────┘  └────────┬───────────┘
                                        │
              ┌─────────────────────────┼──────────────────────────┐
              │                         │                          │
    ┌─────────▼──────┐      ┌──────────▼──────┐      ┌───────────▼──┐
    │  PostgreSQL 15  │      │   Redis 7        │      │  MinIO       │
    │  Port 5432      │      │   Cache/Queue    │      │  Media Store │
    │                 │      │   Port 6379      │      │  Port 9000   │
    │  Tables:        │      │                  │      │              │
    │  - users        │      │  - session cache │      │  Buckets:    │
    │  - content      │      │  - task queue    │      │  - images    │
    │  - knowledge_   │      │  - rate limits   │      │  - videos    │
    │    base         │      └──────────────────┘      └──────────────┘
    │  - approvals    │
    │  - analytics    │
    │  - credentials  │
    │  - schedules    │
    │  - topics       │
    └─────────────────┘

              ┌─────────────────────────────────────────┐
              │              n8n Automation              │
              │           (Port 5678)                   │
              │                                         │
              │  Workflow 1: Weekly Website Crawler      │
              │  Workflow 2: Daily Content Generator     │
              │  Workflow 3: Image Generator             │
              │  Workflow 4: Video Generator             │
              │  Workflow 5: Approval Notifier           │
              │  Workflow 6: Auto Poster (Alt Days)      │
              │  Workflow 7: Analytics Collector         │
              └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    AI AGENT PIPELINE (Daily 9 AM)                   │
│                                                                      │
│  chandigarhdentist.com ──► Knowledge Base                           │
│                                                                      │
│  Agent 1: Content Research                                          │
│  ├── Reads Knowledge Base                                           │
│  ├── Checks Topic History (30-day cooldown)                         │
│  └── Selects 5 unique topics                                        │
│                    ▼                                                 │
│  Agent 2: Content Writer (Claude 3.5 Sonnet)                       │
│  ├── Instagram Post + Caption + 30 Hashtags                         │
│  ├── Facebook Post + Caption + 10 Hashtags                          │
│  └── LinkedIn Post + Caption + 5 Hashtags                           │
│                    ▼                                                 │
│  Agent 3: Video Script Writer (GPT-4o)                              │
│  ├── 5 Reel Scripts (30-60 seconds)                                 │
│  ├── Scene-by-scene breakdown                                       │
│  └── Voiceover + CTA script                                         │
│                    ▼                                                 │
│  Agent 4: Prompt Engineer (GPT-4o)                                  │
│  ├── DALL-E 3 image prompts (per platform aspect ratio)             │
│  └── Kling/Runway/Pika video prompts                                │
│                    ▼                                                 │
│  Agent 5: Video/Image Generator                                     │
│  ├── DALL-E 3 → Images                                              │
│  └── Kling/Runway/Pika → Videos                                     │
│                    ▼                                                 │
│  Agent 6: Approval Manager                                          │
│  ├── Save to PostgreSQL                                             │
│  ├── Send Email notification                                         │
│  └── Send WhatsApp notification                                     │
│                    ▼                                                 │
│  Doctor Review (< 5 min) ──────────────────────────────────────┐   │
│  ├── Approve ─► Schedule for next posting day                   │   │
│  ├── Edit ───► Update caption → Schedule                        │   │
│  ├── Regenerate → Re-runs Agent 2                               │   │
│  └── Reject ─► Archive                                          │   │
│                    ▼                                            │   │
│  Agent 7: Publishing Manager (Alternate Days)     ◄────────────┘   │
│  ├── Post to Instagram (Meta Graph API)                             │
│  ├── Post to Facebook (Meta Graph API)                              │
│  ├── Post to LinkedIn (LinkedIn API v2)                             │
│  ├── Upload to YouTube Shorts (YouTube Data API)                    │
│  └── Post to Google Business Profile                                │
│                    ▼                                                 │
│  Agent 8: Analytics Manager                                         │
│  ├── Collect platform analytics                                     │
│  ├── Store engagement metrics                                       │
│  └── Generate weekly reports                                        │
└─────────────────────────────────────────────────────────────────────┘

DATABASE SCHEMA:
┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────────┐
│   content   │  │ knowledge_   │  │ approvals  │  │  analytics   │
│─────────────│  │    base      │  │────────────│  │──────────────│
│ id (UUID)   │  │──────────────│  │ id         │  │ id           │
│ type        │  │ id           │  │ content_id │  │ content_id   │
│ category    │  │ category     │  │ reviewed_by│  │ platform     │
│ status      │  │ title        │  │ status     │  │ likes        │
│ title       │  │ content      │  │ notes      │  │ comments     │
│ caption     │  │ source_url   │  │ created_at │  │ shares       │
│ hashtags    │  │ tags         │  └────────────┘  │ views        │
│ image_url   │  │ last_crawled │                  │ reach        │
│ video_url   │  └──────────────┘  ┌────────────┐  └──────────────┘
│ image_prompt│                    │ schedules  │
│ video_script│  ┌──────────────┐  │────────────│
│ batch_id    │  │topic_history │  │ content_id │
│ topic_key   │  │──────────────│  │ platform   │
│ platform_ids│  │ topic_key    │  │ scheduled_ │
│ approved_at │  │ topic_name   │  │   for      │
│ published_at│  │ last_used    │  │ status     │
└─────────────┘  │ use_count    │  └────────────┘
                 └──────────────┘
```

## Content Generation Volume

| Daily Output | Count |
|-------------|-------|
| Social Media Posts | 15 (5 topics × 3 platforms) |
| Reel/Video Scripts | 5 |
| AI Image Prompts | 15 |
| AI Video Prompts | 5 |
| Hashtag Sets | 15 |
| Captions | 15 |

**Posted:** 1-2 posts per platform per day (alternate days)  
**Topic uniqueness:** 30-day rolling window  
**Human time required:** < 5 minutes/day
