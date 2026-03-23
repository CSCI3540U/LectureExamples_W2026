import json as json_module
import secrets
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from markupsafe import Markup
from urllib.parse import urlparse
import requests as http_requests

app = Flask(__name__)
app.secret_key = "the wild flamingo dances in the starlight"

stored_comments = []
bank_balance = 1000
transfer_log = []
challenge_email = "victim@example.com"
challenge_last_referer = ""
ssrf_challenge_fetched = set()   # URLs fetched via the SSRF challenge form

# Simulated data

STOCK_PRICES = {
    "AAPL": {"name": "Apple Inc.",       "price": "182.63", "change": "+1.24"},
    "GOOG": {"name": "Alphabet Inc.",    "price": "141.80", "change": "-0.53"},
    "MSFT": {"name": "Microsoft Corp.",  "price": "378.92", "change": "+2.17"},
    "AMZN": {"name": "Amazon.com Inc.",  "price": "186.40", "change": "+0.89"},
}

CURRENCY_RATES = {
    "USD-EUR": {"rate": "0.9201", "name": "US Dollar → Euro"},
    "USD-GBP": {"rate": "0.7893", "name": "US Dollar → British Pound"},
    "USD-JPY": {"rate": "149.42", "name": "US Dollar → Japanese Yen"},
    "USD-CAD": {"rate": "1.3621", "name": "US Dollar → Canadian Dollar"},
}

# Main Page

@app.route("/")
def index():
    return render_template("index.html")

# XSS — Reflected

@app.route("/xss/reflected")
def xss_reflected():
    raw = request.args.get("name", "")
    mode = request.args.get("mode", "vulnerable")

    if mode == "escaped":
        name_display = raw
    else:
        name_display = Markup(raw)

    return render_template(
        "xss_reflected.html",
        name_display=name_display,
        name_input=raw,
        mode=mode,
    )

# XSS — Stored

@app.route("/xss/stored", methods=["GET", "POST"])
def xss_stored():
    mode = request.args.get("mode", "vulnerable")
    if request.method == "POST":
        comment = request.form.get("comment", "")
        stored_comments.append(comment)
        return redirect(url_for("xss_stored", mode=mode))

    if mode == "escaped":
        comments = stored_comments
    else:
        comments = [Markup(c) for c in stored_comments]

    return render_template("xss_stored.html", comments=comments, mode=mode)

@app.route("/xss/stored/clear")
def xss_stored_clear():
    mode = request.args.get("mode", "vulnerable")
    stored_comments.clear()
    return redirect(url_for("xss_stored", mode=mode))

# CSRF — Bank demo

@app.route("/csrf/bank", methods=["GET", "POST"])
def csrf_bank():
    global bank_balance

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    if request.method == "GET":
        mode = request.args.get("mode", session.get("csrf_mode", "vulnerable"))
        session["csrf_mode"] = mode
    else:
        mode = session.get("csrf_mode", "vulnerable")

    csrf_blocked = False
    if request.method == "POST":
        if mode == "protected":
            submitted = request.form.get("csrf_token", "")
            if submitted != session.get("csrf_token"):
                csrf_blocked = True

        if not csrf_blocked:
            amount = int(request.form.get("amount", 0))
            recipient = request.form.get("recipient", "Unknown")
            bank_balance -= amount
            transfer_log.append(f"${amount} → {recipient}")

    status_code = 403 if csrf_blocked else 200
    return render_template(
        "csrf_bank.html",
        balance=bank_balance,
        log=transfer_log,
        mode=mode,
        csrf_token=session.get("csrf_token"),
        csrf_blocked=csrf_blocked,
    ), status_code

@app.route("/csrf/bank/reset")
def csrf_bank_reset():
    global bank_balance
    mode = request.args.get("mode", "vulnerable")
    bank_balance = 1000
    transfer_log.clear()
    return redirect(url_for("csrf_bank", mode=mode))

@app.route("/csrf/evil")
def csrf_evil():
    return render_template("csrf_evil.html")

# CSRF — Challenge

@app.route("/csrf/challenge")
def csrf_challenge():
    return render_template("csrf_challenge.html", email=challenge_email)

@app.route("/csrf/challenge/profile")
def csrf_challenge_profile():
    return render_template("csrf_challenge_profile.html", email=challenge_email)

@app.route("/csrf/challenge/update", methods=["POST"])
def csrf_challenge_update():
    global challenge_email, challenge_last_referer
    challenge_email = request.form.get("email", challenge_email)
    challenge_last_referer = request.headers.get("Referer", "")
    return redirect(url_for("csrf_challenge_profile"))

@app.route("/csrf/challenge/editor", methods=["GET", "POST"])
def csrf_challenge_editor():
    if request.method == "POST":
        session["attack_html"] = request.form.get("html", "")
        return "", 204
    return render_template("csrf_challenge_editor.html", email=challenge_email,
                           attack_html=session.get("attack_html", ""))

@app.route("/csrf/challenge/preview")
def csrf_challenge_preview():
    placeholder = (
        "<body style='font-family:monospace;background:#111;color:#555;"
        "display:flex;align-items:center;justify-content:center;height:100vh;margin:0'>"
        "<p>No attack deployed yet.</p></body>"
    )
    return session.get("attack_html", placeholder), 200, {"Content-Type": "text/html"}

@app.route("/csrf/challenge/reset")
def csrf_challenge_reset():
    global challenge_email, challenge_last_referer
    challenge_email = "victim@example.com"
    challenge_last_referer = ""
    session.pop("attack_html", None)
    return redirect(url_for("csrf_challenge"))

@app.route("/api/csrf-challenge/status")
def csrf_challenge_status():
    solved = (challenge_email == "pwned@csrf.attack"
              and "/csrf/challenge/preview" in challenge_last_referer)
    return jsonify({"email": challenge_email, "solved": solved})

@app.route("/api/flag/csrf-challenge")
def flag_csrf_challenge():
    if challenge_email != "pwned@csrf.attack":
        return jsonify({"error": "The victim's email hasn't been changed to the target yet."}), 403
    if "/csrf/challenge/preview" not in challenge_last_referer:
        return jsonify({"error": "Email was changed, but not via a forged request — use the attack editor."}), 403
    return jsonify({"flag": "FLAG{csrf_y0u_f0rg3d_1t}"})

# SSRF — Internal simulated microservices

@app.route("/internal/stocks/<ticker>")
def internal_stocks(ticker):
    if ticker.upper() not in STOCK_PRICES:
        return "", 404
    if not _is_ssrf_request():
        return jsonify({"error": "This API is not accessible to the outside!"}), 403
    data = STOCK_PRICES.get(ticker.upper())
    return jsonify({"ticker": ticker.upper(), **data, "currency": "USD"})

def _is_ssrf_request():
    """Return True only when the request was made by the Flask server itself via SSRF."""
    return request.headers.get("X-Internal-Request") == "ssrf"

@app.route("/internal/currency/", strict_slashes=False)
def internal_currency_index():
    """Poorly secured index — lists all available endpoints including admin."""
    if not _is_ssrf_request():
        return jsonify({"error": "This API is not accessible to the outside!"}), 403
    return jsonify({
        "service": "CurrencyService v2.1",
        "endpoints": [
            f"/internal/currency/{pair}" for pair in CURRENCY_RATES
        ],
    })

@app.route("/internal/currency/<pair>")
def internal_currency(pair):
    # Unknown paths return empty 404 so fuzzers can distinguish real endpoints
    if pair != "admin" and pair.upper() not in CURRENCY_RATES:
        return "", 404
    if not _is_ssrf_request():
        return jsonify({"error": "This API is not accessible to the outside!"}), 403
    if pair == "admin":
        return jsonify({
            "service": "CurrencyService Admin",
            "db_host": "currency-db.internal:5432",
            "db_pass": "Curr3ncy$3cr3t!",
            "api_key": "curr-live-sk-9f8e7d6c5b4a",
            "note": "Internal use only — not reachable from the public internet.",
        })
    data = CURRENCY_RATES.get(pair.upper())
    return jsonify({"pair": pair.upper(), **data})

# SSRF — Stock price demo

@app.route("/ssrf", methods=["GET", "POST"])
def ssrf():
    result = error = fetched_url = stock_data = None
    mode = request.args.get("mode", "vulnerable")
    selected_ticker = request.form.get("ticker", "AAPL").upper()

    if request.method == "POST":
        if mode == "protected":
            # Safe: look up the ticker locally — never make an outbound HTTP request
            data = STOCK_PRICES.get(selected_ticker)
            if data:
                price_dict = {"ticker": selected_ticker, **data, "currency": "USD"}
                result = json_module.dumps(price_dict, indent=2)
                stock_data = price_dict
            else:
                error = f"Unknown ticker symbol: {selected_ticker}"
        else:
            # Vulnerable: fetch whatever URL is in the hidden field
            fetched_url = request.form.get("url", "").strip()
            try:
                resp = http_requests.get(fetched_url, timeout=5,
                                         headers={"X-Internal-Request": "ssrf"})
                result = resp.text[:3000]
                try:
                    parsed = json_module.loads(result)
                    if "ticker" in parsed and "price" in parsed:
                        stock_data = parsed
                except (ValueError, KeyError):
                    pass
            except Exception as exc:
                error = str(exc)

    return render_template(
        "ssrf.html",
        result=result, error=error, fetched_url=fetched_url,
        stock_data=stock_data, selected_ticker=selected_ticker,
        mode=mode, tickers=list(STOCK_PRICES.keys()),
    )

# SSRF — Currency exchange challenge

@app.route("/ssrf/challenge", methods=["GET", "POST"])
def ssrf_challenge():
    result = error = fetched_url = rate_data = None
    selected_pair = request.form.get("pair", "USD-EUR").upper()

    if request.method == "POST":
        fetched_url = request.form.get("url", "").strip()
        ssrf_challenge_fetched.add(fetched_url)
        try:
            resp = http_requests.get(fetched_url, timeout=5,
                                     headers={"X-Internal-Request": "ssrf"})
            result = resp.text[:3000]
            try:
                parsed = json_module.loads(result)
                if "pair" in parsed and "rate" in parsed:
                    rate_data = parsed
            except (ValueError, KeyError):
                pass
        except Exception as exc:
            error = str(exc)

    return render_template(
        "ssrf_challenge.html",
        result=result, error=error, fetched_url=fetched_url,
        rate_data=rate_data, selected_pair=selected_pair,
        pairs=list(CURRENCY_RATES.keys()),
    )

@app.route("/ssrf/challenge/reset")
def ssrf_challenge_reset():
    ssrf_challenge_fetched.clear()
    return redirect(url_for("ssrf_challenge"))

# Flag API

@app.route("/api/flag/xss-reflected")
def flag_xss_reflected():
    referer = request.headers.get("Referer", "")
    if "/xss/reflected" in referer:
        return jsonify({"flag": "FLAG{r3fl3ct3d_xss_1s_fun}"})
    return jsonify({"error": "Exploit the vulnerability to retrieve this flag."}), 403

@app.route("/api/flag/xss-stored")
def flag_xss_stored():
    referer = request.headers.get("Referer", "")
    if "/xss/stored" in referer:
        return jsonify({"flag": "FLAG{st0r3d_xss_p3rs1sts}"})
    return jsonify({"error": "Exploit the vulnerability to retrieve this flag."}), 403

@app.route("/api/flag/csrf")
def flag_csrf():
    if any("Attacker" in entry for entry in transfer_log):
        return jsonify({"flag": "FLAG{csrf_1s_s1l3nt}"})
    return jsonify({"error": "Trigger the CSRF attack first — visit the evil page."}), 403

@app.route("/api/flag/ssrf-challenge")
def flag_ssrf_challenge():
    if any("/internal/currency/admin" in url for url in ssrf_challenge_fetched):
        return jsonify({"flag": "FLAG{ssrf_curr3ncy_pwn3d}"})
    return jsonify({"error": "Access the internal admin endpoint via SSRF first."}), 403

if __name__ == "__main__":
    app.run(debug=True, port=5000)