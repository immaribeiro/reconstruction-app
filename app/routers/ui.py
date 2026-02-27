from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/costs", response_class=HTMLResponse)
async def costs_page(request: Request):
    return templates.TemplateResponse("costs.html", {"request": request})

@router.get("/reminders", response_class=HTMLResponse)
async def reminders_page(request: Request):
    return templates.TemplateResponse("reminders.html", {"request": request})
