import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(duration, 4))
        print(f"[Timer] {request.method} {request.url.path} - {duration:.4f}s")
        return response
