# Order Tracking & Shipping System

## How to Run

```bash
chmod +x start.sh   # first time only
./start.sh
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |

Place `order.xlsx` and `SKU.xlsx` in the project root before starting.

---

## Dependencies

**Backend** (Python, managed via `uv`)

| Package | Purpose |
|---------|---------|
| `fastapi` + `uvicorn` | Web framework and ASGI server |
| `httpx` | Async HTTP client for external API calls |
| `openpyxl` | Read xlsx input files (order.xlsx, SKU.xlsx, mock-product.xlsx) |
| `pydantic` | Request/response schema validation |
| `python-dotenv` | Load environment variables from `.env` |
| `pytest` + `pytest-asyncio` | Unit testing |

**Frontend** (Node.js, managed via `npm`)

| Package | Purpose |
|---------|---------|
| `react` + `react-dom` | UI framework |
| `react-router-dom` | Client-side routing |
| `vite` (v5) | Dev server and bundler |
| `axios` | HTTP client for backend API calls |

---

## Assumptions

### Input Data

Both files must be placed in the project root.

**`order.xlsx`** — one row per order:

| Column | Example |
|--------|---------|
| `OrderNo` | `PO-20251130-00072` |
| `OrderDate` | `30/11/25` |
| `Status` | `Completed` |
| `CompanyName` | `ABC Pharmacy` |
| `CustomerName` | `John Smith` |
| `PhoneNumber` | `0412345678` |
| `Email` | `john@abcpharma.com.au` |
| `Address` | `123 Main St, Sydney NSW 2000` |

**`SKU.xlsx`** — one row per SKU line item, multiple rows can share the same `OrderNumber`:

| Column | Example | Notes |
|--------|---------|-------|
| `SKU` | `NUBKIKP10` | Product code, looked up in product data source |
| `QTY` | `2` | Quantity ordered |
| `AssignedTracking` | `1` | Internal auto-increment ID |
| `TrackingNo` | `2FWZ00006498987` | Carrier tracking number used for logistics queries |
| `OrderNumber` | `PO-20251130-00072` | Foreign key linking to `order.xlsx` |

### Product Data

- Product details (name, RRP, weight/dimensions) are fetched from a Google Sheet via `GOOGLE_SHEET_URL` in `.env`.
- If the Google Sheet is unreachable (auth failure, timeout, network error), the system automatically falls back to `mock-product.xlsx`, which contains 10 sample products for testing.

### Pricing Calculation

```
Subtotal = Σ (RRP × QTY)
GST      = Subtotal × 10%
Total    = Subtotal + GST + Shipment Fee
```

### Shipment Fee

Shipping origin is fixed at postcode `2111` (Ryde, NSW). Destination postcode and state are parsed from the order's `Address` field.

1. **AusPost Prices API** — calls `POST /prices/items` with item weight and postcodes. Uses product `7E05` (Parcel Post domestic). Price field: `calculated_price`.
2. **Formula fallback** — used automatically when the AusPost API is unavailable: `$10.00 base + total_volumetric_kg × $2.00`. The frontend shows a footnote when the fallback is active.

### Carrier Detection & Tracking

Carrier is identified from the tracking number format before any API call:

| Pattern | Example | Carrier | How it's tracked |
|---------|---------|---------|-----------------|
| Starts with `2FWZ` | `2FWZ00006498987` | StarTrack/AusPost | AusPost Shipping API + web link |
| Two letters + digits + `AU` | `EE123456789AU` | AusPost | AusPost Shipping API |
| Pure numeric | `305506914` | TNT | TNT web-tracking URL |
| Anything else | — | Unknown | Try AusPost → TNT → mark unknown |

StarTrack is an AusPost subsidiary and shares the same API (`GET /shipments/{id}/summary` with Basic Auth). A direct web-tracking link is always included for StarTrack results.

TNT does not provide a public tracking API. The system generates a web-tracking link (`tnt.com/...?cons=<TrackingNo>`) and returns it directly for the user to visit.

> **Note:** The tracking numbers in the provided test data (`SKU.xlsx`) are fictional. Clicking TNT or StarTrack/AusPost tracking links may show "Not Found" on the carrier's website — this is expected behaviour with dummy data.

Tracking is queried in real-time on every request — there is no local cache.
