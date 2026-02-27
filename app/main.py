from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import create_db_and_tables, get_db # Import get_db
from sqlalchemy.orm import Session # Corrected import
from app.config import settings
from app.auth import get_api_key

# Import all routers
from app.routers import costs, reminders, food, training, mental, summary, dashboard, ui

app = FastAPI(
    title="House Reconstruction Management API",
    description="API for managing house reconstruction data",
    version="0.1.0",
)

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Middleware for API Key authentication
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Skip auth for health check and UI routes
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        try:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != settings.api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key",
                )
        except HTTPException as e:
            # For API requests, return JSON error
            if request.url.path.startswith("/api/"):
                return JSONResponse(content={"detail": e.detail}, status_code=e.status_code)
            # For other routes, still fallback to HTML or default
            return HTMLResponse(content=e.detail, status_code=e.status_code)
    
    response = await call_next(request)
    return response

# Health check endpoint (no auth required)
@app.get("/api/health", tags=["monitoring"])
async def health_check():
    return {"status": "ok"}

# Include API routers
app.include_router(costs.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(food.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(mental.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# Include UI router (no prefix)
app.include_router(ui.router)