"""Unit tests for order_service."""
import pytest
from unittest.mock import patch, AsyncMock
from services.order_service import list_orders, get_order_detail

MOCK_ORDER = {
    "OrderNo": "PO-20251130-00072",
    "OrderDate": "30/11/25",
    "Status": "Completed",
    "CompanyName": "ABC Pharmacy",
    "CustomerName": "John Smith",
    "PhoneNumber": "0412345678",
    "Email": "john@abcpharma.com.au",
    "Address": "123 Main St, Sydney NSW 2000",
}

MOCK_SKUS = [
    {"SKU": "NUBKIKP10", "QTY": 2, "AssignedTracking": "EE123456789AU", "OrderNumber": "PO-20251130-00072"},
    {"SKU": "GROOGKU10", "QTY": 1, "AssignedTracking": "EE123456789AU", "OrderNumber": "PO-20251130-00072"},
]

MOCK_PRODUCT = {
    "sku": "NUBKIKP10",
    "product_name": "Kikuya Peak THC 25% Flower 10g",
    "rrp": 120.00,
    "volumetric_gross_weight_kg": 0.2,
}

MOCK_TRACKING = {
    "EE123456789AU": {"tracking_no": "EE123456789AU", "company": "AusPost", "status": "Delivered"}
}


class TestListOrders:
    @patch("services.order_service.get_all_orders", return_value=[MOCK_ORDER])
    def test_returns_list(self, mock_orders):
        result = list_orders()
        assert isinstance(result, list)
        assert result[0]["OrderNo"] == "PO-20251130-00072"


class TestGetOrderDetail:
    @pytest.mark.asyncio
    @patch("services.order_service.resolve_tracking_for_order", new_callable=AsyncMock, return_value=MOCK_TRACKING)
    @patch("services.order_service.get_product_by_sku", return_value=MOCK_PRODUCT)
    @patch("services.order_service.get_skus_by_order", return_value=MOCK_SKUS)
    @patch("services.order_service.get_order_by_no", return_value=MOCK_ORDER)
    async def test_order_found(self, mock_order, mock_skus, mock_product, mock_tracking):
        result = await get_order_detail("PO-20251130-00072")
        assert result is not None
        assert result["order"]["OrderNo"] == "PO-20251130-00072"
        assert result["subtotal"] > 0
        assert result["gst"] == pytest.approx(result["subtotal"] * 0.10, abs=0.01)
        assert result["total"] == pytest.approx(
            result["subtotal"] + result["gst"] + result["shipment_fee"], abs=0.01
        )

    @pytest.mark.asyncio
    @patch("services.order_service.get_order_by_no", return_value=None)
    async def test_order_not_found(self, mock_order):
        result = await get_order_detail("NONEXISTENT")
        assert result is None
