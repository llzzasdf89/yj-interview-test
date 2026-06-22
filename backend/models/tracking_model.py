"""
Tracking Model — async calls to AusPost/StarTrack API, TNT web-linking.
Tracking is queried in real-time on every request (no local cache).

Carrier detection (by tracking number format):
  StarTrack/AusPost — starts with "2FWZ" (e.g. 2FWZ00006498987)
  AusPost           — matches /^[A-Z]{2}\d+AU$/i (e.g. EE123456789AU)
  TNT               — pure numeric (e.g. 305506914)
  Unknown           — anything else
"""
import os
import re
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

AUSPOST_API_KEY = os.getenv("AUSPOST_API_KEY", "8ba91b84-ca46-40e6-9680-77e55e3c5942")
AUSPOST_PASSWORD = os.getenv("AUSPOST_PASSWORD", "kE1Rt1ualfjjL2ESLLB4")
AUSPOST_BASE_URL = os.getenv(
    "AUSPOST_BASE_URL",
    "https://digitalapi.auspost.com.au/test/shipping/v1",
)
TNT_TRACKING_BASE = "https://www.tnt.com/express/en_au/site/tracking.html"
STARTRACK_TRACKING_BASE = "https://auspost.com.au/mypost/beta/track/#/search"


# ─── Carrier detection ────────────────────────────────────────────────────────

_STARTRACK_RE = re.compile(r"^2FWZ", re.IGNORECASE)   # StarTrack/AusPost
_AUSPOST_RE = re.compile(r"^[A-Za-z]{2}\d+AU$", re.IGNORECASE)
_TNT_RE = re.compile(r"^\d+$")                         # pure numeric → TNT


def detect_carrier(tracking_no: str) -> str:
    """
    Return carrier code based on tracking number format:
      'startrack' — starts with 2FWZ  (StarTrack, queried via AusPost API)
      'auspost'   — two letters + digits + AU
      'tnt'       — pure numeric
      'unknown'   — anything else
    """
    t = tracking_no or ""
    if _STARTRACK_RE.match(t):
        return "startrack"
    if _AUSPOST_RE.match(t):
        return "auspost"
    if _TNT_RE.match(t):
        return "tnt"
    return "unknown"


# ─── AusPost ─────────────────────────────────────────────────────────────────

async def _query_auspost(tracking_no: str, company: str = "AusPost") -> Optional[dict]:
    try:
        url = f"{AUSPOST_BASE_URL}/shipments/{tracking_no}/summary"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                auth=(AUSPOST_API_KEY, AUSPOST_PASSWORD),
                headers={"Content-Type": "application/json"},
                timeout=8,
            )
        if resp.status_code == 200:
            data = resp.json()
            shipment = data.get("shipments", [{}])[0] if data.get("shipments") else {}
            status_obj = shipment.get("status", {})
            status = (
                status_obj.get("description", "Unknown")
                if isinstance(status_obj, dict)
                else str(status_obj or "Unknown")
            )
            # Extract last update timestamp — try status.date, then first event date
            last_update = None
            if isinstance(status_obj, dict):
                last_update = status_obj.get("date")
            if not last_update:
                events = shipment.get("events") or shipment.get("trackSummary", {}).get("events", [])
                if events and isinstance(events[0], dict):
                    last_update = events[0].get("date") or events[0].get("timestamp")
            return {
                "tracking_no": tracking_no,
                "company": company,
                "status": status,
                "last_update": last_update,
            }
    except Exception:
        pass
    return None


# ─── StarTrack ────────────────────────────────────────────────────────────────

async def _query_startrack(tracking_no: str) -> Optional[dict]:
    """
    StarTrack is an AusPost subsidiary — tracking is queried via the same
    AusPost Shipping API. The company label is set to 'StarTrack/AusPost'
    and a web-tracking URL is always included so users can view live status.
    """
    tracking_url = f"{STARTRACK_TRACKING_BASE}?searchTerm={tracking_no}"
    result = await _query_auspost(tracking_no, company="StarTrack/AusPost")
    if result:
        result["tracking_url"] = tracking_url
        return result
    # API unavailable — return web-link fallback so the frontend can still link out
    return {
        "tracking_no": tracking_no,
        "company": "StarTrack/AusPost",
        "status": "Not Available",
        "tracking_url": tracking_url,
    }


# ─── TNT ─────────────────────────────────────────────────────────────────────

def _query_tnt(tracking_no: str) -> dict:
    """
    TNT tracking page is JavaScript-rendered — server-side requests cannot parse
    whether a consignment exists. Return the web-tracking link unconditionally
    and let the user check live status on tnt.com.
    """
    return {
        "tracking_no": tracking_no,
        "company": "TNT",
        "status": "View on TNT website",
        "tracking_url": f"{TNT_TRACKING_BASE}?cons={tracking_no}",
        "last_update": None,
    }


# ─── Public API ──────────────────────────────────────────────────────────────

async def fetch_tracking(assigned_tracking: str) -> dict:
    """
    Route to the correct carrier by tracking number format:

      2FWZ...   → StarTrack/AusPost (AusPost API + web-link)
      XX...AU   → AusPost API only
      numeric   → TNT web-link
      other     → best-effort AusPost → TNT → Unknown
    """
    carrier = detect_carrier(assigned_tracking)

    if carrier == "startrack":
        return await _query_startrack(assigned_tracking)

    if carrier == "auspost":
        result = await _query_auspost(assigned_tracking)
        return result or {
            "tracking_no": assigned_tracking,
            "company": "AusPost",
            "status": "Not Available",
        }

    if carrier == "tnt":
        return _query_tnt(assigned_tracking)

    # Unknown format — best-effort
    result = await _query_auspost(assigned_tracking)
    if result:
        return result
    result = _query_tnt(assigned_tracking)
    if result:
        return result
    return {
        "tracking_no": assigned_tracking,
        "company": "Unknown",
        "status": "Not Available",
    }


