from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users, categories

app = FastAPI(
    title="My Todo API",
    description="This API manages TODO items with filtering, completion, and pagination.",
    version="1.0.0",
    contact={"name": "ook2 Developer", "email": "dhwpdnr21@kakao.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(categories.router)
