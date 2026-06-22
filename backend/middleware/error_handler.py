import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from middleware.logging_handler import write_log
from datetime import datetime


async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    write_log({
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "level": "ERROR",
        "path": request.url.path,
        "error": str(exc),
        "type": type(exc).__name__,
    })
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "system error", "success": False},
    )
