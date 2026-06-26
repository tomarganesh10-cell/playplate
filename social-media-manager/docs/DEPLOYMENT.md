# Deployment Guide — Playplate AI Social Media Manager
## Hostinger VPS Deployment

---

## Prerequisites

- Hostinger VPS (Ubuntu 22.04 LTS, minimum 4 vCPU, 8GB RAM, 100GB SSD)
- Domain: `social.playplate.in` pointing to VPS IP via Cloudflare
- SSH access to root

---

## Step 1: DNS Setup (Cloudflare)

1. Go to Cloudflare → DNS → Add Record
   ```
   Type: A
   Name: social
   Content: YOUR_VPS_IP
   Proxy: DNS only (grey cloud) initially
   TTL: Auto
   ```
2. Wait for DNS propagation (5-30 minutes)
3. Verify: `ping social.playplate.in`

---

## Step 2: VPS Initial Setup

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Clone the repository
git clone https://github.com/YOUR_REPO/playplate-smm.git /opt/playplate-smm
cd /opt/playplate-smm/social-media-manager

# Run one-shot setup
chmod +x deploy/setup.sh
./deploy/setup.sh
```

---

## Step 3: Configure Environment

```bash
nano /opt/playplate-smm/social-media-manager/.env
```

**Minimum required for basic operation:**
```env
SECRET_KEY=<generated_automatically>
POSTGRES_PASSWORD=<generated_automatically>
OPENAI_API_KEY=sk-...          # For content generation
ANTHROPIC_API_KEY=sk-ant-...   # For content writing
SENDGRID_API_KEY=SG.xxx        # For email notifications
DOCTOR_EMAIL=dr.anshu@chandigarhdentist.com
DOCTOR_WHATSAPP=+91XXXXXXXXXX
```

After editing:
```bash
docker-compose restart backend
```

---

## Step 4: Add API Keys via Admin Panel

1. Open: `https://social.playplate.in/admin`
2. Login: `admin@social.playplate.in` / `admin123`
3. Go to **API Credentials**
4. Add keys in this priority order:
   - ✅ OpenAI API Key (required — content generation)
   - ✅ Anthropic Claude API (required — content writing)
   - ✅ SendGrid API (required — email notifications)
   - ⚡ Meta Access Token (for Instagram/Facebook posting)
   - ⚡ LinkedIn Access Token (for LinkedIn posting)
   - ⚡ Kling/Runway/Pika (for AI video generation)
   - ⚡ WhatsApp API (for WhatsApp notifications)

---

## Step 5: Initialize Knowledge Base

```bash
# Seed with built-in dental knowledge
curl -X POST https://social.playplate.in/api/knowledge-base/seed \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Crawl the website for additional content
curl -X POST https://social.playplate.in/api/knowledge-base/crawl \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Or via Admin Panel → Knowledge Base → "Seed KB" + "Re-crawl Site"

---

## Step 6: Test Content Generation

```bash
# Trigger manual generation
curl -X POST https://social.playplate.in/api/content/generate/daily \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Or via Admin Panel → Dashboard → "Generate Now"

Then go to: `https://social.playplate.in/client/approval`

---

## Step 7: Import n8n Workflows

1. Open: `https://social.playplate.in/n8n`
2. Login with your n8n credentials
3. Go to: Settings → Import → Import from File
4. Import all files from: `n8n/workflows/`
5. Configure credentials in n8n:
   - Email (SMTP or SendGrid)
   - Twilio (WhatsApp)
   - HTTP Header Auth (API Token)
6. Activate workflows

---

## Step 8: Verify Automatic Scheduling

n8n workflows run automatically:
- **9:00 AM IST** — Daily content generation
- **Alternate days** — Auto-posting approved content
- **Weekly (Monday)** — Website re-crawl
- **Daily 2:00 AM** — Database backup

Check workflow status: n8n → Executions tab

---

## Step 9: Enable Cloudflare Proxy (Optional)

After SSL is confirmed working:
1. Cloudflare → DNS → Toggle to orange cloud (proxied)
2. Cloudflare → SSL/TLS → Full (Strict)
3. Cloudflare → Security → Bot Fight Mode: ON
4. Add Page Rule: Rate limit `/api/auth/*` to 5 requests/minute

---

## Architecture Overview

```
Internet → Cloudflare CDN/WAF
         → Nginx (SSL Termination)
         → [Frontend: React SPA on port 80]
         → [API: FastAPI on port 8000]
         → [n8n: Workflows on port 5678]
         → [PostgreSQL: Database on port 5432]
         → [Redis: Cache/Queue on port 6379]
         → [MinIO: Media Storage on port 9000]
```

---

## Service URLs

| Service | Internal | External |
|---------|----------|----------|
| Frontend | `frontend:80` | `https://social.playplate.in/` |
| Backend API | `backend:8000` | `https://social.playplate.in/api/` |
| API Docs | - | `https://social.playplate.in/api/docs` |
| n8n | `n8n:5678` | `https://social.playplate.in/n8n/` |
| Admin Panel | - | `https://social.playplate.in/admin` |
| Client Dashboard | - | `https://social.playplate.in/client` |
| MinIO Console | `minio:9001` | VPN/SSH Tunnel only |

---

## Monitoring

```bash
# View all logs
docker-compose logs -f

# Check service health
docker-compose ps

# Resource usage
docker stats

# Database size
docker exec postgres psql -U smm -d smm_db -c "\l+"
```

---

## Backup & Restore

```bash
# Manual backup
make backup

# Restore
docker exec -i postgres psql -U smm smm_db < backup_YYYYMMDD.sql

# Automated: runs daily at 2 AM, keeps 7 days
# Location: /opt/backups/
```

---

## Troubleshooting

**Backend won't start:**
```bash
docker-compose logs backend
docker-compose restart backend
```

**n8n workflows not running:**
```bash
docker-compose logs n8n
# Check timezone: should be Asia/Kolkata
```

**Content not generating:**
- Check AI API keys in Admin → Credentials
- Check logs: `docker-compose logs backend | grep "Daily Workflow"`

**SSL issues:**
```bash
docker-compose run --rm certbot
docker-compose restart nginx
```
