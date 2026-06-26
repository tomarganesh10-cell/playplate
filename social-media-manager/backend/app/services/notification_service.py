"""
Notification Service — Email, WhatsApp, Dashboard notifications.
"""
import httpx
from loguru import logger
from jinja2 import Template
from app.config import settings


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }
    .header h1 { color: white; margin: 0; font-size: 24px; }
    .header p { color: rgba(255,255,255,0.9); margin: 5px 0 0; }
    .body { padding: 30px; }
    .stats { display: flex; gap: 15px; margin: 20px 0; }
    .stat-card { flex: 1; background: #f8f9ff; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #e8ecff; }
    .stat-number { font-size: 28px; font-weight: bold; color: #667eea; }
    .stat-label { color: #666; font-size: 13px; margin-top: 5px; }
    .btn { display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           color: white; text-decoration: none; text-align: center; padding: 15px 30px;
           border-radius: 8px; font-size: 16px; font-weight: bold; margin: 25px 0; }
    .footer { background: #f8f9ff; padding: 20px; text-align: center; color: #999; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🦷 Daily Content Ready!</h1>
      <p>Your AI-generated dental content is waiting for approval</p>
    </div>
    <div class="body">
      <p>Good morning, <strong>Dr. Anshu Gupta</strong>! 🌟</p>
      <p>Your AI Social Media Manager has generated today's content batch. Please review and approve to schedule posting.</p>

      <div class="stats">
        <div class="stat-card">
          <div class="stat-number">{{ post_count }}</div>
          <div class="stat-label">Posts Ready</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ video_count }}</div>
          <div class="stat-label">Videos Ready</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">&lt; 5 min</div>
          <div class="stat-label">Review Time</div>
        </div>
      </div>

      <p>✅ Approve posts you like<br>
         ✏️ Edit captions if needed<br>
         🔄 Regenerate if needed<br>
         ❌ Reject what doesn't fit</p>

      <a href="{{ dashboard_url }}/approval?batch={{ batch_id }}" class="btn">
        👆 Review Today's Content
      </a>

      <p style="color: #999; font-size: 13px;">
        Batch ID: {{ batch_id }}<br>
        Generated: {{ timestamp }}
      </p>
    </div>
    <div class="footer">
      <p>Playplate AI Social Media Manager | social.playplate.in</p>
      <p>For Dr. Anshu Gupta | chandigarhdentist.com</p>
    </div>
  </div>
</body>
</html>
"""


class NotificationService:
    async def send_email(self, to: str, subject: str, html_body: str) -> bool:
        """Send email via SendGrid or SMTP."""
        if settings.SENDGRID_API_KEY:
            return await self._send_via_sendgrid(to, subject, html_body)
        return await self._send_via_smtp(to, subject, html_body)

    async def _send_via_sendgrid(self, to: str, subject: str, html_body: str) -> bool:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "personalizations": [{"to": [{"email": to}]}],
                        "from": {"email": settings.FROM_EMAIL, "name": "Playplate SMM"},
                        "subject": subject,
                        "content": [{"type": "text/html", "value": html_body}],
                    },
                )
                success = response.status_code in (200, 202)
                if not success:
                    logger.error(f"SendGrid error: {response.status_code} {response.text}")
                return success
            except Exception as e:
                logger.error(f"Email send error: {e}")
                return False

    async def _send_via_smtp(self, to: str, subject: str, html_body: str) -> bool:
        """Fallback SMTP send."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.FROM_EMAIL
            msg["To"] = to
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.FROM_EMAIL, to, msg.as_string())
            return True
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    async def send_whatsapp(self, phone: str, message: str) -> bool:
        """Send WhatsApp message via Twilio or WhatsApp Business API."""
        if not settings.WHATSAPP_API_KEY:
            logger.warning("WhatsApp not configured")
            return False

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{settings.WHATSAPP_PHONE_NUMBER}/Messages.json",
                    auth=(settings.WHATSAPP_PHONE_NUMBER, settings.WHATSAPP_API_KEY),
                    data={
                        "From": f"whatsapp:{settings.WHATSAPP_PHONE_NUMBER}",
                        "To": f"whatsapp:{phone}",
                        "Body": message,
                    },
                )
                return response.status_code in (200, 201)
            except Exception as e:
                logger.error(f"WhatsApp send error: {e}")
                return False

    async def send_daily_approval_notification(
        self, batch_id: str, post_count: int, video_count: int
    ) -> None:
        """Send all notifications for daily content approval."""
        from datetime import datetime

        template = Template(EMAIL_TEMPLATE)
        html_body = template.render(
            post_count=post_count,
            video_count=video_count,
            batch_id=batch_id,
            dashboard_url=settings.CLIENT_URL,
            timestamp=datetime.utcnow().strftime("%d %B %Y, %I:%M %p UTC"),
        )

        # Email
        await self.send_email(
            to=settings.DOCTOR_EMAIL,
            subject=f"🦷 {post_count} Posts + {video_count} Videos Ready for Approval — Playplate SMM",
            html_body=html_body,
        )

        # WhatsApp
        whatsapp_msg = (
            f"🦷 *Daily Content Ready!*\n\n"
            f"Dr. Anshu Gupta, your AI Social Media Manager has generated today's content:\n\n"
            f"✅ {post_count} Social Posts\n"
            f"🎬 {video_count} Video Scripts\n\n"
            f"Please review and approve:\n"
            f"{settings.CLIENT_URL}/approval?batch={batch_id}\n\n"
            f"_Less than 5 minutes to review!_ 🚀"
        )
        await self.send_whatsapp(settings.DOCTOR_WHATSAPP, whatsapp_msg)
        logger.info(f"Approval notifications sent for batch {batch_id}")
