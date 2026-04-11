# Bitly — Link Shortener

A lightning-fast, highly concurrent link management web application built using **FastAPI** and **Amazon DynamoDB**.

## Features
- **Server-Side Rendered:** Jinja2 templates tightly coupled with FastAPI endpoints for seamless server-side views.
- **Robust Storage:** Data scales identically from a local test container straight into AWS using fully automated schema migrations using Boto3.
- **Modular MVC Design:** Cleanly encapsulates routes, utilities, layouts, and data abstraction logic.

## Setup

First, initialize your environment by installing the package prerequisites:
```bash
# Optional but recommended, activate a virtual environment
pip install -r requirements.txt
```

### Starting the Database

This application utilizes **DynamoDB**. We highly recommend using `amazon/dynamodb-local` Docker container for local development:
```bash
docker run --rm -p 8000:8000 amazon/dynamodb-local:latest -jar DynamoDBLocal.jar -inMemory -sharedDb
```

### Running the Server

Start up the backend application with specific mocked AWS environment variables mapped to your local database container running at port `8000`. The server runs using `uvicorn` on `5000`:
```bash
DYNAMODB_ENDPOINT_URL=http://localhost:8000 AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy AWS_DEFAULT_REGION=us-east-1 uvicorn main:app --port 5000 --reload
```

Then open [http://localhost:5000](http://localhost:5000).

## Project Structure

```
bitly/
├── main.py              # Application entrypoint & middlewares
├── config.py            # Global setups (Jinja2)
├── db.py                # Boto3 configurations and wrapper functions
├── utils.py             # User password hashing and session utilities
├── routers/             # FastApi functional paths
│   ├── auth.py          # /login, /signup, /logout endpoints
│   └── urls.py          # /dashboard, and /{short_code} URL redirects
├── requirements.txt     # Python dependencies
├── templates/           # Jinja2 templates (base, login, dashboard)
└── static/              # CSS styling assets
```
