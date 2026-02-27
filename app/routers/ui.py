from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
async def read_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@router.get("/reminders", response_class=HTMLResponse)
async def read_reminders(request: Request):
    return templates.TemplateResponse("reminders.html", {"request": request})

@router.get("/costs", response_class=HTMLResponse)
async def read_costs(request: Request):
    return templates.TemplateResponse("costs.html", {"request": request})

@router.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})