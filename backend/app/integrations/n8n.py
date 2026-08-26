import httpx

from app.core.config import get_settings


async def notify_n8n(payload: dict):
    url = get_settings().n8n_webhook_url
    if not url:
        return {"sent": False, "reason": "N8N_WEBHOOK_URL not configured"}
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
    return {"sent": True}
