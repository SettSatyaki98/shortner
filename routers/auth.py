from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from config import templates
from utils import flash, hash_password
from db import get_user_by_email, create_user
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, email: str = Form(""), password: str = Form("")):
    email = email.strip().lower()
    if not email or not password:
        flash(request, 'Please fill in all fields.', 'error')
        return templates.TemplateResponse("login.html", {"request": request})

    user = get_user_by_email(email)
    if user and user.get('password') == hash_password(password):
        request.session["user"] = {"name": user["name"], "email": user["email"]}
        logger.info(f"User '{email}' logged in successfully.")
        flash(request, 'Login successful!', 'success')
        return RedirectResponse(url="/dashboard", status_code=303)
    
    logger.warning(f"Failed login attempt for '{email}'.")
    flash(request, 'Invalid email or password.', 'error')
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, name: str = Form(""), email: str = Form(""), password: str = Form(""), confirm_password: str = Form("")):
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password or not confirm_password:
        flash(request, 'Please fill in all fields.', 'error')
        return templates.TemplateResponse("signup.html", {"request": request})

    if len(password) < 6:
        flash(request, 'Password must be at least 6 characters.', 'error')
        return templates.TemplateResponse("signup.html", {"request": request})

    if password != confirm_password:
        flash(request, 'Passwords do not match.', 'error')
        return templates.TemplateResponse("signup.html", {"request": request})

    if get_user_by_email(email):
        flash(request, 'An account with this email already exists.', 'error')
        return templates.TemplateResponse("signup.html", {"request": request})

    create_user(email, name, hash_password(password))
    logger.info(f"New user registered: '{email}'")

    request.session["user"] = {"name": name, "email": email}
    flash(request, 'Account created successfully!', 'success')
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    flash(request, 'Signed out successfully.', 'success')
    return RedirectResponse(url="/login", status_code=303)
