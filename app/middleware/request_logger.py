import json
import time
import traceback
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import AppLogger

logger = AppLogger().get_logger()


async def request_logger(request: Request, call_next: Callable):
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time.perf_counter()

    # Process the request
    response = await call_next(request)
    # Log response details
    process_time = (time.perf_counter() - start_time)
    logger.info(f"Response: Status {response.status_code} processed in {process_time:.2f}ms")
    response.headers["X-Process-Time"] = str(process_time)
    return response


class RequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await request_logger(request, call_next)
        except Exception as e:
            stacktrace = traceback.format_exc()
            logger.error(json.dumps({"stacktrace": stacktrace}))
            raise e from e
