import hashlib
from fastapi import Request

def flash(request: Request, message: str, category: str = "success"):
    """Adds a flash message to the current session."""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request, with_categories=False):
    """Retrieves and clears flash messages from the session for rendering."""
    messages = request.session.pop("_messages", [])
    if with_categories:
        return [(m['category'], m['message']) for m in messages]
    return [m['message'] for m in messages]

def hash_password(password: str) -> str:
    """Hashes a password with SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
