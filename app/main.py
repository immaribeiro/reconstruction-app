from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables
from app.config import settings

from app.routers import costs, reminders, dashboard, ui

app = FastAPI(
    title="House Reconstruction Management",
    description="Track costs, payments and progress for house reconstruction",
    version="0.2.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != settings.api_key:
            return JSONResponse(content={"detail": "Invalid API Key"}, status_code=401)
    return await call_next(request)


@app.get("/api/health", tags=["monitoring"])
async def health_check():
    return {"status": "ok"}


# API routers
app.include_router(costs.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# UI
app.include_router(ui.router)
