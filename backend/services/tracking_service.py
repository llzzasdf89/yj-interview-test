"""
Tracking Service — async resolution with concurrent gather for multiple refs.
Tracking is queried in real-time on every request.
"""
import asyncio
from models.tracking_model import fetch_tracking


async def resolve_tracking_for_order(sku_rows: list[dict]) -> dict[str, dict]:
    """
    Resolve all unique TrackingNo values for an order concurrently.
    Returns a dict keyed by TrackingNo (the actual carrier tracking number).
    """
    unique_nos = list({
        row["tracking_no"]
        for row in sku_rows
        if row.get("tracking_no")
    })

    results = await asyncio.gather(
        *[fetch_tracking(no) for no in unique_nos],
        return_exceptions=False,
    )

    return dict(zip(unique_nos, results))
