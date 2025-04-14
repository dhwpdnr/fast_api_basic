from fastapi import FastAPI, Request
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users, categories
import logging
from .logging_config import LOGGING_CONFIG, dictConfig
import time
from .middleware import TimerMiddleware

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="My Todo API",
    description="This API manages TODO items with filtering, completion, and pagination.",
    version="1.0.0",
    contact={"name": "ook2 Developer", "email": "dhwpdnr21@kakao.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

app.add_middleware(TimerMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Exception while handling request: {e}")
        raise

    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} in {process_time:.2f}s")
    return response


Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(categories.router)
