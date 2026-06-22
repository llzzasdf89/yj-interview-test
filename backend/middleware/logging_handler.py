import json
import time
import os
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


def _get_log_path() -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{date_str}.log")


def write_log(record: dict):
    with open(_get_log_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        response = await call_next(request)

        duration_ms = round((time.time() - start) * 1000, 2)
        record = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status": response.status_code,
            "duration_ms": duration_ms,
        }
        write_log(record)
        return response
