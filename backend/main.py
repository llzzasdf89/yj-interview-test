from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware.request_id_middleware import RequestIdMiddleware
from middleware.logging_handler import LoggingMiddleware
from middleware.error_handler import global_error_handler
from routers.order_router import router as order_router
from routers.tracking_router import router as tracking_router

app = FastAPI(
    title="Order Tracking & Shipping API",
    description="Order details, SKU pricing, tracking and shipment fee estimation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware (order matters: first added = outermost wrapper) ──────────────
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global exception handler ────────────────────────────────────────────────
app.add_exception_handler(Exception, global_error_handler)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(order_router)
app.include_router(tracking_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
