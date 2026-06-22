"""
Order Service — assembles a complete order response by orchestrating
models and other services. Fully async: tracking + shipment fee run concurrently.
"""
import asyncio
from typing import Optional
from models.order_model import get_all_orders, get_order_by_no, get_skus_by_order
from models.product_model import get_product_by_sku
from services.calculation_service import calculate_order_totals
from services.tracking_service import resolve_tracking_for_order


def list_orders() -> list[dict]:
    """Return all order headers (for the list page). Sync — reads local xlsx only."""
    return get_all_orders()


async def get_order_detail(order_no: str) -> Optional[dict]:
    """
    Returns a fully assembled order dict including:
    - order header
    - SKU line items with product details + pricing
    - tracking info (resolved concurrently with shipment fee)
    - calculated totals
    """
    order = get_order_by_no(order_no)
    if not order:
        return None

    sku_rows = get_skus_by_order(order_no)

    # Enrich each SKU row with product details from Google Sheet / mock
    enriched_lines = []
    for row in sku_rows:
        sku_code = row.get("SKU", "")
        qty = int(row.get("QTY", 0))
        product = get_product_by_sku(sku_code) or {}
        enriched_lines.append({
            "sku": sku_code,
            "qty": qty,
            "assigned_tracking": row.get("AssignedTracking"),   # internal ID
            "tracking_no": row.get("TrackingNo", ""),           # carrier tracking number
            "product_name": product.get("product_name", sku_code),
            "rrp": product.get("rrp", 0.0),
            "volumetric_gross_weight_kg": product.get("volumetric_gross_weight_kg", 0.0),
            "image_url": product.get("image_url"),
        })

    # Run tracking resolution and shipment fee calculation concurrently
    address = order.get("Address", "")
    calculation_task = calculate_order_totals(enriched_lines, dest_address=address)
    tracking_task = resolve_tracking_for_order(enriched_lines)

    calculation, tracking_map = await asyncio.gather(calculation_task, tracking_task)

    return {
        "order": order,
        "line_items": calculation["line_items"],
        "tracking": tracking_map,
        "subtotal": calculation["subtotal"],
        "gst": calculation["gst"],
        "shipment_fee": calculation["shipment_fee"],
        "shipment_fee_method": calculation["shipment_fee_method"],
        "total": calculation["total"],
    }
