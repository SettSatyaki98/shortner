# Bitly — Link Shortener

A Flask-based link management app with server-side authentication.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open [http://localhost:5000](http://localhost:5000).

## Demo Account

- **Email:** admin@bitly.com
- **Password:** password123

## Project Structure

```
bitly/
├── app.py               # Flask application (routes, auth, user store)
├── requirements.txt     # Python dependencies
├── templates/           # Jinja2 templates
│   ├── base.html        # Shared layout (orbs, flash messages, fonts)
│   ├── login.html       # Sign-in page
│   ├── signup.html      # Account creation page
│   └── dashboard.html   # Authenticated dashboard
└── static/
    └── css/
        └── styles.css   # Design system & shared styles
```
