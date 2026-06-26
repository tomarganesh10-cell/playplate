from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
import base64

from app.database import get_db
from app.models.credential import Credential
from app.routers.auth import require_admin
from app.models.user import User

router = APIRouter(prefix="/credentials", tags=["credentials"])

CREDENTIAL_DEFINITIONS = [
    {"service": "openai", "label": "OpenAI API", "key_name": "OPENAI_API_KEY"},
    {"service": "anthropic", "label": "Anthropic Claude API", "key_name": "ANTHROPIC_API_KEY"},
    {"service": "gemini", "label": "Google Gemini API", "key_name": "GEMINI_API_KEY"},
    {"service": "meta", "label": "Meta (Facebook/Instagram) API", "key_name": "META_ACCESS_TOKEN"},
    {"service": "linkedin", "label": "LinkedIn API", "key_name": "LINKEDIN_ACCESS_TOKEN"},
    {"service": "youtube", "label": "YouTube Data API", "key_name": "YOUTUBE_REFRESH_TOKEN"},
    {"service": "google_drive", "label": "Google Drive API", "key_name": "GOOGLE_SERVICE_ACCOUNT_JSON"},
    {"service": "google_sheets", "label": "Google Sheets API", "key_name": "GOOGLE_SHEETS_ID"},
    {"service": "whatsapp", "label": "WhatsApp Business API", "key_name": "WHATSAPP_API_KEY"},
    {"service": "sendgrid", "label": "SendGrid Email API", "key_name": "SENDGRID_API_KEY"},
    {"service": "kling", "label": "Kling AI Video", "key_name": "KLING_API_KEY"},
    {"service": "runway", "label": "Runway ML Video", "key_name": "RUNWAY_API_KEY"},
    {"service": "pika", "label": "Pika Labs Video", "key_name": "PIKA_API_KEY"},
    {"service": "hailuo", "label": "Hailuo AI Video", "key_name": "HAILUO_API_KEY"},
    {"service": "stability", "label": "Stability AI (Images)", "key_name": "STABILITY_API_KEY"},
    {"service": "google_veo", "label": "Google Veo Video", "key_name": "GOOGLE_VEO_API_KEY"},
]


class CredentialUpdate(BaseModel):
    value: str
    extra_data: Optional[str] = None


@router.get("/")
async def list_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all credential definitions with their configuration status."""
    result = await db.execute(select(Credential))
    saved = {c.service: c for c in result.scalars().all()}

    credentials = []
    for defn in CREDENTIAL_DEFINITIONS:
        saved_cred = saved.get(defn["service"])
        credentials.append({
            "service": defn["service"],
            "label": defn["label"],
            "key_name": defn["key_name"],
            "is_configured": saved_cred.is_configured if saved_cred else False,
            "is_active": saved_cred.is_active if saved_cred else False,
            "last_verified": saved_cred.last_verified.isoformat() if saved_cred and saved_cred.last_verified else None,
        })

    return credentials


@router.put("/{service}")
async def update_credential(
    service: str,
    data: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Save or update a credential (value is stored base64-encoded for basic obfuscation)."""
    defn = next((d for d in CREDENTIAL_DEFINITIONS if d["service"] == service), None)
    if not defn:
        raise HTTPException(404, "Unknown credential service")

    result = await db.execute(select(Credential).where(Credential.service == service))
    cred = result.scalar_one_or_none()

    # Basic encoding (in production use proper encryption like Fernet)
    encoded_value = base64.b64encode(data.value.encode()).decode()

    if cred:
        cred.encrypted_value = encoded_value
        cred.is_configured = bool(data.value)
        cred.is_active = bool(data.value)
        cred.extra_data = data.extra_data
    else:
        cred = Credential(
            service=service,
            label=defn["label"],
            key_name=defn["key_name"],
            encrypted_value=encoded_value,
            is_configured=bool(data.value),
            is_active=bool(data.value),
            extra_data=data.extra_data,
        )
        db.add(cred)

    await db.commit()

    # Update runtime settings
    import os
    os.environ[defn["key_name"]] = data.value

    return {"message": f"{defn['label']} credential saved"}


@router.delete("/{service}")
async def delete_credential(
    service: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Credential).where(Credential.service == service))
    cred = result.scalar_one_or_none()
    if cred:
        cred.encrypted_value = None
        cred.is_configured = False
        cred.is_active = False
        await db.commit()
    return {"message": "Credential removed"}
