from fastapi.templating import Jinja2Templates

# Initialize Jinja2Templates. It is configured here to avoid circular imports.
templates = Jinja2Templates(directory="templates")

# AWS Global Configurations
AWS_REGION = "us-east-1"

# Application Server Configurations
HOST = "127.0.0.1"
PORT = 5000
RELOAD = True
