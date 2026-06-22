"""
Calculation Service — Subtotal, GST, Shipment Fee, Total.

Shipment fee priority:
  1. AusPost Prices API (async)
  2. Fallback formula: total_kg × $2.00 + $10.00 base
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
AUSPOST_ACCOUNT = os.getenv("AUSPOST_ACCOUNT_NUMBER", "2004456017")
ORIGIN_POSTCODE = "2111"  # Ryde NSW
ORIGIN_SUBURB = "Ryde"
ORIGIN_STATE = "NSW"

AU_STATES = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]


def _extract_postcode(address: str) -> Optional[str]:
    """Parse a 4-digit AU postcode from an address string."""
    match = re.search(r"\b(\d{4})\b", address or "")
    return match.group(1) if match else None


def _extract_state(address: str) -> str:
    """Best-effort parse of Australian state abbreviation from address string."""
    upper = (address or "").upper()
    for state in AU_STATES:
        if re.search(rf"\b{state}\b", upper):
            return state
    return ""


async def _auspost_shipping_rate(
    total_kg: float,
    dest_postcode: Optional[str],
    dest_state: str = "",
) -> Optional[float]:
    """
    Call AusPost /prices/items to get a shipping rate (async).
    Payload uses top-level `from` / `to` address objects as required by the API.
    Returns fee in AUD or None if the call fails.
    """
    if not dest_postcode:
        return None
    try:
        payload = {
            "from": {
                "suburb": ORIGIN_SUBURB,
                "state": ORIGIN_STATE,
                "postcode": ORIGIN_POSTCODE,
                "country": "AU",
            },
            "to": {
                "suburb": "",
                "state": dest_state,
                "postcode": dest_postcode,
                "country": "AU",
            },
            "items": [
                {
                    "item_reference": "SHIP001",
                    "product_id": "7E05",       # AusPost Parcel Post domestic
                    "length": 10,
                    "width": 10,
                    "height": 10,
                    "weight": max(total_kg, 0.1),
                }
            ],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AUSPOST_BASE_URL}/prices/items",
                json=payload,
                auth=(AUSPOST_API_KEY, AUSPOST_PASSWORD),
                headers={
                    "Content-Type": "application/json",
                    "Account-Number": AUSPOST_ACCOUNT,
                },
                timeout=8,
            )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                prices = items[0].get("prices", [])
                if prices:
                    # Prefer the product we requested (7E05 Parcel Post);
                    # fall back to the cheapest available option.
                    preferred = next(
                        (p for p in prices if p.get("product_id") == "7E05"), None
                    )
                    price_info = preferred or min(
                        prices, key=lambda p: p.get("calculated_price", float("inf"))
                    )
                    total_price = price_info.get("calculated_price")
                    if total_price is not None:
                        return float(total_price)
    except Exception:
        pass
    return None


def _fallback_shipping_rate(total_kg: float) -> float:
    """Simple weight-based formula when AusPost API is unavailable."""
    base = 10.0
    per_kg = 2.0
    return round(base + total_kg * per_kg, 2)


async def calculate_shipment_fee(
    sku_lines: list[dict],
    dest_address: Optional[str] = None,
) -> tuple[float, str]:
    """
    Returns (shipment_fee, method_used).
    method_used is 'auspost_api' or 'formula'.
    """
    total_kg = sum(
        line.get("volumetric_gross_weight_kg", 0.0) * line.get("qty", 0)
        for line in sku_lines
    )
    dest_postcode = _extract_postcode(dest_address) if dest_address else None
    dest_state = _extract_state(dest_address) if dest_address else ""

    fee = await _auspost_shipping_rate(total_kg, dest_postcode, dest_state)
    if fee is not None:
        return fee, "auspost_api"

    return _fallback_shipping_rate(total_kg), "formula"


async def calculate_order_totals(
    sku_lines: list[dict],
    dest_address: Optional[str] = None,
) -> dict:
    """
    sku_lines: list of dicts with keys: sku, product_name, rrp, qty,
               volumetric_gross_weight_kg
    Returns full calculation breakdown.
    """
    line_items = []
    for line in sku_lines:
        unit_price = line.get("rrp", 0.0)
        qty = line.get("qty", 0)
        line_total = round(unit_price * qty, 2)
        line_items.append({
            **line,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    subtotal = round(sum(li["line_total"] for li in line_items), 2)
    gst = round(subtotal * 0.10, 2)
    shipment_fee, fee_method = await calculate_shipment_fee(sku_lines, dest_address)
    total = round(subtotal + gst + shipment_fee, 2)

    return {
        "line_items": line_items,
        "subtotal": subtotal,
        "gst": gst,
        "shipment_fee": shipment_fee,
        "shipment_fee_method": fee_method,
        "total": total,
    }
