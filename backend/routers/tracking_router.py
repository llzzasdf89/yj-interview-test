from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from models.tracking_model import fetch_tracking

router = APIRouter(prefix="/api/tracking", tags=["Tracking"])


class TrackingResponse(BaseModel):
    tracking_no: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    tracking_url: Optional[str] = None
    last_update: Optional[str] = None


@router.get(
    "/{tracking_ref}",
    response_model=TrackingResponse,
    summary="Query tracking status for a given tracking number",
)
async def get_tracking(tracking_ref: str):
    return await fetch_tracking(tracking_ref)
