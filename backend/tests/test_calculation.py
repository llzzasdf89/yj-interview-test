"""Unit tests for calculation_service."""
import pytest
from unittest.mock import patch, AsyncMock
from services.calculation_service import (
    calculate_order_totals,
    calculate_shipment_fee,
    _extract_postcode,
    _fallback_shipping_rate,
)

SAMPLE_LINES = [
    {"sku": "NUBKIKP10", "qty": 2, "rrp": 120.00, "volumetric_gross_weight_kg": 0.2, "product_name": "Kikuya Peak"},
    {"sku": "GROOGKU10", "qty": 1, "rrp": 150.00, "volumetric_gross_weight_kg": 0.1, "product_name": "OG Kush"},
]


class TestExtractPostcode:
    def test_valid_postcode(self):
        assert _extract_postcode("123 Main St, Sydney NSW 2000") == "2000"

    def test_no_postcode(self):
        assert _extract_postcode("No postcode here") is None

    def test_none_address(self):
        assert _extract_postcode(None) is None

    def test_melbourne_postcode(self):
        assert _extract_postcode("45 George St, Melbourne VIC 3000") == "3000"


class TestFallbackShippingRate:
    def test_zero_weight(self):
        assert _fallback_shipping_rate(0.0) == 10.0

    def test_one_kg(self):
        assert _fallback_shipping_rate(1.0) == 12.0

    def test_half_kg(self):
        assert _fallback_shipping_rate(0.5) == 11.0


class TestCalculateOrderTotals:
    @pytest.mark.asyncio
    async def test_subtotal(self):
        result = await calculate_order_totals(SAMPLE_LINES)
        assert result["subtotal"] == 390.00

    @pytest.mark.asyncio
    async def test_gst_is_10_percent(self):
        result = await calculate_order_totals(SAMPLE_LINES)
        assert result["gst"] == pytest.approx(result["subtotal"] * 0.10, abs=0.01)

    @pytest.mark.asyncio
    async def test_total_equals_sum(self):
        result = await calculate_order_totals(SAMPLE_LINES)
        expected = result["subtotal"] + result["gst"] + result["shipment_fee"]
        assert result["total"] == pytest.approx(expected, abs=0.01)

    @pytest.mark.asyncio
    async def test_line_totals(self):
        result = await calculate_order_totals(SAMPLE_LINES)
        lines = result["line_items"]
        assert lines[0]["line_total"] == 240.00
        assert lines[1]["line_total"] == 150.00

    @pytest.mark.asyncio
    @patch("services.calculation_service._auspost_shipping_rate", new_callable=AsyncMock, return_value=15.50)
    async def test_auspost_rate_used_when_available(self, mock_rate):
        result = await calculate_order_totals(SAMPLE_LINES, dest_address="Sydney NSW 2000")
        assert result["shipment_fee"] == 15.50
        assert result["shipment_fee_method"] == "auspost_api"

    @pytest.mark.asyncio
    @patch("services.calculation_service._auspost_shipping_rate", new_callable=AsyncMock, return_value=None)
    async def test_fallback_when_auspost_fails(self, mock_rate):
        result = await calculate_order_totals(SAMPLE_LINES, dest_address="Sydney NSW 2000")
        assert result["shipment_fee_method"] == "formula"
        assert result["shipment_fee"] > 0
