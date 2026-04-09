"""
Bitly — Flask Application
Handles authentication (signup, login, logout) with server-side sessions.
User data is stored in a simple JSON file for demo purposes.
"""

import os
import json
import hashlib
import secrets
import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ---------- Simple JSON-based store ----------

DATA_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
URLS_FILE = os.path.join(os.path.dirname(__file__), 'urls.json')


def _load_urls():
    if not os.path.exists(URLS_FILE):
        return []
    with open(URLS_FILE, 'r') as f:
        return json.load(f)

def _save_urls(urls):
    with open(URLS_FILE, 'w') as f:
        json.dump(urls, f, indent=2)


def _load_users():
    """Load all users from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def _save_users(users):
    """Write all users to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def _hash_password(password):
    """Hash a password with SHA-256 (simple demo — use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


# Seed a demo user on first run
def _seed_demo():
    users = _load_users()
    if not any(u['email'] == 'admin@bitly.com' for u in users):
        users.append({
            'name': 'Admin',
            'email': 'admin@bitly.com',
            'password': _hash_password('password123')
        })
        _save_users(users)


_seed_demo()


# ---------- Auth decorator ----------

def login_required(f):
    """Redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Please sign in to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ---------- Routes ----------

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')

        users = _load_users()
        user = next(
            (u for u in users
             if u['email'] == email and u['password'] == _hash_password(password)),
            None
        )

        if user:
            session['user'] = {'name': user['name'], 'email': user['email']}
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validation
        if not name or not email or not password or not confirm:
            flash('Please fill in all fields.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        users = _load_users()
        if any(u['email'] == email for u in users):
            flash('An account with this email already exists.', 'error')
            return render_template('signup.html')

        # Create user
        users.append({
            'name': name,
            'email': email,
            'password': _hash_password(password)
        })
        _save_users(users)

        # Auto-login
        session['user'] = {'name': name, 'email': email}
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = session['user']
    if request.method == 'POST':
        long_url = request.form.get('long_url', '').strip()
        if not long_url:
            flash('Please enter a valid URL.', 'error')
            return redirect(url_for('dashboard'))
        
        # Basic validation / normalization
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url
            
        short_code = secrets.token_urlsafe(4)
        
        urls = _load_urls()
        urls.append({
            'long_url': long_url,
            'short_code': short_code,
            'userid': user['email'],
            'sysdate': datetime.datetime.utcnow().isoformat()
        })
        _save_urls(urls)
        flash('URL shortened successfully!', 'success')
        return redirect(url_for('dashboard'))

    # GET request
    all_urls = _load_urls()
    user_urls = [u for u in all_urls if u['userid'] == user['email']]
    # Sort by descending sysdate
    user_urls.sort(key=lambda x: x.get('sysdate', ''), reverse=True)
    
    # Passing request.host_url so we can form full short links in template
    return render_template('dashboard.html', user=user, urls=user_urls, host_url=request.host_url)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Signed out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/<short_code>')
def redirect_short_url(short_code):
    urls = _load_urls()
    for u in urls:
        if u['short_code'] == short_code:
            return redirect(u['long_url'])
    
    flash('Short URL not found.', 'error')
    return redirect(url_for('index'))


# ---------- Run ----------


if __name__ == '__main__':
    app.run(debug=True, port=5000)
