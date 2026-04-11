import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import templates
from utils import get_flashed_messages
from db import setup_dynamodb_tables
from routers import auth, urls

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to initialize the backend tables
    setup_dynamodb_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Add session support using a fast cryptographically secure backend key
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# Static mount (CSS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Expose global messages utility to the Jinja templates
templates.env.globals['get_flashed_messages'] = get_flashed_messages

# Include our separated routing logic
app.include_router(auth.router)
app.include_router(urls.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
