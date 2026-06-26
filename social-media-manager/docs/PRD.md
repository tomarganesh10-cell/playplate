# Product Requirements Document
# AI Social Media Manager — Dr. Anshu Gupta (Chandigarh Dentist)

**Version:** 1.0.0  
**Domain:** social.playplate.in  
**Client:** Dr. Anshu Gupta — Cosmetic & Aesthetic Dentist, Implantologist, Pediatric Dentist  
**Website:** https://www.chandigarhdentist.com  
**Experience:** 27+ Years  

---

## 1. Executive Summary

A fully automated AI-powered social media management system deployed on Hostinger VPS. The system crawls the client's website, builds a knowledge base, generates daily content (posts, reels, videos), manages an approval workflow, and auto-posts to all major platforms — with less than 5 minutes of human effort per day.

---

## 2. System Overview

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python 3.11) |
| Frontend Dashboard | React 18 + Tailwind CSS |
| Automation Engine | n8n (self-hosted) |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 |
| AI Content | OpenAI GPT-4o + Claude 3.5 Sonnet |
| Image Gen | DALL-E 3 + Stable Diffusion |
| Video Gen | Google Veo / Kling / Runway / Pika / Hailuo |
| Web Scraper | Crawlee + Playwright |
| Deployment | Docker + Docker Compose + Nginx |
| SSL | Let's Encrypt (Certbot) |
| CDN/DNS | Cloudflare |
| Monitoring | Prometheus + Grafana |
| Storage | Google Drive API + Local MinIO |

---

## 3. User Roles

| Role | Access | Description |
|------|--------|-------------|
| Super Admin | /admin | Full system access, credential management |
| Client (Doctor) | /client | View, approve, reject, edit content |
| Viewer | /client/view | Read-only analytics access |

---

## 4. Content Types

### Social Posts
- Instagram Feed Post (1:1, 4:5, 1.91:1)
- Facebook Post
- LinkedIn Post
- Google Business Profile Post

### Video Content
- Instagram Reels (9:16, 15-60s)
- YouTube Shorts (9:16, up to 60s)
- Educational Videos (various lengths)

### Content Categories
1. Dental Awareness
2. Myth vs Fact
3. Patient Education
4. Smile Makeover
5. Kids Dentistry
6. Dental Implants
7. Braces & Orthodontics
8. Teeth Whitening
9. Oral Hygiene Tips
10. Patient Journey / Testimonials
11. Doctor Introduction
12. Clinic Tour
13. FAQ Videos
14. Festival Posts
15. Local Chandigarh Content
16. Before/After Educational

---

## 5. Daily Workflow (9:00 AM Trigger)

```
09:00 AM → Trigger
  ↓
Content Research Agent (pulls from knowledge base, checks topic history)
  ↓
Content Writer Agent (generates 5 posts + captions + hashtags)
  ↓
Prompt Engineer Agent (creates image/video prompts)
  ↓
Image Generator (DALL-E 3 / Stable Diffusion)
  ↓
Video Script Writer Agent (5 reel scripts)
  ↓
Video Generator Agent (Kling/Runway/Pika)
  ↓
Store in PostgreSQL + Google Sheets
  ↓
Approval Manager (Email + WhatsApp + Dashboard notification)
  ↓
Doctor Reviews on Dashboard
  ↓
If Approved → Publishing Manager (scheduled on alternate days)
  ↓
Analytics Manager (tracks engagement, generates weekly reports)
```

---

## 6. Posting Rules

- Generate content daily
- Post on alternate days (to avoid oversaturation)
- Never repeat topics within 30 days
- Track all posted topics in database
- Optimal posting times per platform:
  - Instagram: 9 AM, 12 PM, 6 PM IST
  - Facebook: 9 AM, 3 PM IST
  - LinkedIn: 8 AM, 12 PM IST
  - YouTube Shorts: 9 AM, 5 PM IST

---

## 7. AI Agents

| Agent | Model | Responsibility |
|-------|-------|---------------|
| Content Research | GPT-4o | Pulls relevant topics from KB, checks what's trending |
| Content Writer | Claude 3.5 Sonnet | Writes posts, captions, hashtags |
| Video Script Writer | GPT-4o | Creates video scripts with scenes, voiceover, CTA |
| Prompt Engineer | GPT-4o | Optimizes prompts for image/video generators |
| Video Generator | Kling/Runway/Pika API | Generates 9:16 videos |
| Approval Manager | Rule-based | Sends notifications, manages approval state |
| Publishing Manager | Rule-based + API | Posts to platforms at optimal times |
| Analytics Manager | GPT-4o | Analyzes engagement, generates insights |

---

## 8. Dashboard Screens

### Admin (/admin)
- System Overview & Health
- All Clients Management
- Credential Management (API keys)
- n8n Workflow Status
- System Logs
- Backup & Restore

### Client (/client)
- Dashboard Overview (stats, upcoming posts)
- Content Calendar
- Approval Queue (Approve / Reject / Edit / Regenerate)
- Posts Library
- Videos Library
- Analytics & Engagement
- Settings (notification preferences)

---

## 9. Infrastructure Requirements

| Service | Port | Description |
|---------|------|-------------|
| Frontend (Nginx) | 80/443 | React SPA |
| Backend API | 8000 | FastAPI |
| n8n | 5678 | Workflow automation |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & queues |
| MinIO | 9000 | Media storage |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |

---

## 10. Success Metrics

- Content generation time: < 30 minutes daily
- Human review time: < 5 minutes daily
- Posting reliability: 99.9% uptime
- Content uniqueness: 0% topic repetition within 30 days
- Platform coverage: 5 platforms simultaneously
