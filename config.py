from fastapi.templating import Jinja2Templates

# Initialize Jinja2Templates. It is configured here to avoid circular imports.
templates = Jinja2Templates(directory="templates")
