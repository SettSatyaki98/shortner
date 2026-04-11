import secrets
import datetime
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from config import templates
from utils import flash
from db import fetch_user_urls_desc, create_url, get_url_by_short_code

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        flash(request, 'Please sign in to continue.', 'error')
        return RedirectResponse(url="/login", status_code=303)

    user_urls = fetch_user_urls_desc(user['email'])
    host_url = str(request.base_url)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "urls": user_urls,
        "host_url": host_url
    })

@router.post("/dashboard", response_class=HTMLResponse)
async def dashboard_post(request: Request, long_url: str = Form("")):
    user = request.session.get("user")
    if not user:
        flash(request, 'Please sign in to continue.', 'error')
        return RedirectResponse(url="/login", status_code=303)

    long_url = long_url.strip()
    if not long_url:
        flash(request, 'Please enter a valid URL.', 'error')
        return RedirectResponse(url="/dashboard", status_code=303)
    
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url
        
    short_code = secrets.token_urlsafe(4)
    sysdate = datetime.datetime.utcnow().isoformat()
    
    create_url(short_code, long_url, user['email'], sysdate)
    
    flash(request, 'URL shortened successfully!', 'success')
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/{short_code}")
async def redirect_short_url(request: Request, short_code: str):
    if short_code == "favicon.ico":
        raise HTTPException(status_code=404)
        
    url_item = get_url_by_short_code(short_code)
    if url_item:
        return RedirectResponse(url=url_item['long_url'], status_code=303)
        
    flash(request, 'Short URL not found.', 'error')
    return RedirectResponse(url="/", status_code=303)
