from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.order_service import list_orders, get_order_detail

router = APIRouter(prefix="/api/orders", tags=["Orders"])


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class OrderSummary(BaseModel):
    OrderNo: str
    OrderDate: Optional[str]
    Status: Optional[str]
    CompanyName: Optional[str]
    CustomerName: Optional[str]
    PhoneNumber: Optional[str]
    Email: Optional[str]
    Address: Optional[str]


class LineItem(BaseModel):
    sku: str
    product_name: str
    qty: int
    unit_price: float
    line_total: float
    assigned_tracking: Optional[int] = None   # internal auto-increment ID
    tracking_no: Optional[str] = None          # carrier tracking number
    image_url: Optional[str] = None


class TrackingInfo(BaseModel):
    tracking_no: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    tracking_url: Optional[str] = None
    last_update: Optional[str] = None


class OrderDetailResponse(BaseModel):
    order: OrderSummary
    line_items: list[LineItem]
    tracking: dict[str, TrackingInfo]
    subtotal: float
    gst: float
    shipment_fee: float
    shipment_fee_method: str
    total: float


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[OrderSummary], summary="List all orders")
def get_orders():
    return list_orders()


@router.get(
    "/{order_no}",
    response_model=OrderDetailResponse,
    summary="Get full order detail",
)
async def get_order(order_no: str):
    detail = await get_order_detail(order_no)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Order {order_no} not found")
    return detail
