"""Unit tests for tracking_model and tracking_service."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from models.tracking_model import _query_auspost, _query_tnt, fetch_tracking, detect_carrier
from services.tracking_service import resolve_tracking_for_order


class TestDetectCarrier:
    def test_startrack(self):
        assert detect_carrier("2FWZ00006498987") == "startrack"

    def test_auspost(self):
        assert detect_carrier("EE123456789AU") == "auspost"

    def test_tnt(self):
        assert detect_carrier("305506914") == "tnt"

    def test_unknown(self):
        assert detect_carrier("UNKNOWN123") == "unknown"


class TestQueryAuspost:
    @pytest.mark.asyncio
    async def test_successful_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "shipments": [{"status": {"description": "Delivered"}}]
        }
        mock_session = MagicMock()
        mock_session.get = AsyncMock(return_value=mock_resp)

        with patch("models.tracking_model.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await _query_auspost("EE123456789AU")

        assert result is not None
        assert result["company"] == "AusPost"
        assert result["status"] == "Delivered"

    @pytest.mark.asyncio
    async def test_exception_returns_none(self):
        with patch("models.tracking_model.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__ = AsyncMock(side_effect=Exception("timeout"))
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await _query_auspost("BAD_TRACKING")

        assert result is None


class TestQueryTnt:
    def test_returns_link(self):
        result = _query_tnt("305506914")
        assert result["company"] == "TNT"
        assert result["status"] == "View on TNT website"
        assert "305506914" in result["tracking_url"]
        assert result["last_update"] is None


class TestFetchTracking:
    @pytest.mark.asyncio
    @patch("models.tracking_model._query_auspost", new_callable=AsyncMock, return_value=None)
    async def test_auspost_not_found_returns_not_available(self, mock_query):
        result = await fetch_tracking("EE123456789AU")
        assert result["company"] == "AusPost"
        assert result["status"] == "Not Available"

    @pytest.mark.asyncio
    async def test_tnt_returns_link(self):
        result = await fetch_tracking("305506914")
        assert result["company"] == "TNT"
        assert "tracking_url" in result


class TestResolveTrackingForOrder:
    @pytest.mark.asyncio
    @patch("services.tracking_service.fetch_tracking", new_callable=AsyncMock, return_value={
        "tracking_no": "EE123456789AU", "company": "AusPost", "status": "Delivered"
    })
    async def test_unique_nos_only(self, mock_fetch):
        sku_rows = [
            {"tracking_no": "EE123456789AU"},
            {"tracking_no": "EE123456789AU"},  # duplicate
        ]
        result = await resolve_tracking_for_order(sku_rows)
        assert len(result) == 1
        mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    @patch("services.tracking_service.fetch_tracking", new_callable=AsyncMock, return_value={
        "tracking_no": "EE123456789AU", "company": "AusPost", "status": "Delivered"
    })
    async def test_skips_empty_tracking_no(self, mock_fetch):
        sku_rows = [
            {"tracking_no": "EE123456789AU"},
            {"tracking_no": ""},
            {"tracking_no": None},
        ]
        result = await resolve_tracking_for_order(sku_rows)
        assert len(result) == 1
