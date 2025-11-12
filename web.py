# web.py
import os
import logging
import random
import string
from flask import Flask, render_template_string, request, jsonify

# Configure logging so Render logs show details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try safe import of tgbot (so import error messages are clearer)
try:
    from tgbot import send_message_to_admin
except Exception as e:
    # create a stub so the app can start and show a clear error when used
    logger.exception("Failed to import tgbot.send_message_to_admin: %s", e)

    def send_message_to_admin(bot_token, admin_id, message):
        logger.error("tgbot import failed; cannot send. Called with token=%s admin=%s message=%s",
                     bot_token, admin_id, message)
        return False

app = Flask(__name__)

# Simple in-memory store for links (keeps things simple for free Render)
BOT_LINKS = {}

# Home page template
HOME_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Telegram Link Generator</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;background:#0f1720;color:#fff;text-align:center;padding:50px;">
  <h1>Telegram Link Generator</h1>
  <form method="POST">
    <input name="admin_id" placeholder="Admin ID" required style="padding:8px;width:320px;margin:6px"><br>
    <input name="bot_token" placeholder="Bot Token" required style="padding:8px;width:320px;margin:6px"><br>
    <button type="submit" style="padding:10px 20px">Generate Link</button>
  </form>
  {% if link %}
    <div style="margin-top:20px;background:rgba(255,255,255,0.05);display:inline-block;padding:12px;border-radius:8px;">
      <strong>Your link:</strong><br>
      <a href="{{ link }}" style="color:#50fa7b" target="_blank">{{ link }}</a>
    </div>
  {% endif %}
  <p style="margin-top:18px;color:#aab3bf;font-size:13px">API: /link/admin{admin_id}&token{bot_token}</p>
</body>
</html>
"""

# Send page template
SEND_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Send Messages</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;background:#0b1220;color:#fff;text-align:center;padding:50px;">
  <h1>Send Message to Admin</h1>
  <form method="POST">
    <textarea name="msg1" required placeholder="Message 1" style="width:360px;height:80px;padding:8px;margin:8px"></textarea><br>
    <textarea name="msg2" required placeholder="Message 2" style="width:360px;height:80px;padding:8px;margin:8px"></textarea><br>
    <button type="submit" style="padding:10px 20px">Send Both Messages</button>
  </form>
  {% if message %}
    <div style="margin-top:18px;color:#50fa7b"><strong>{{ message }}</strong></div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    link = None
    if request.method == "POST":
        admin_id = (request.form.get("admin_id") or "").strip()
        bot_token = (request.form.get("bot_token") or "").strip()
        if not admin_id or not bot_token:
            return render_template_string(HOME_HTML, link=None)
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        BOT_LINKS[key] = {"admin": admin_id, "token": bot_token}
        link = request.url_root.rstrip("/") + f"/send/{key}"
        logger.info("Generated link %s for admin %s", link, admin_id)
    return render_template_string(HOME_HTML, link=link)

@app.route("/link/admin<admin_id>&token<bot_token>", methods=["GET"])
def api_generate_link(admin_id, bot_token):
    """API endpoint for generating links:
       /link/admin{admin_id}&token{bot_token}
    """
    admin_id = str(admin_id or "").strip()
    bot_token = str(bot_token or "").strip()
    if not admin_id or not bot_token:
        return jsonify({"status":"error","message":"admin_id and bot_token required"}), 400

    key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    BOT_LINKS[key] = {"admin": admin_id, "token": bot_token}
    link = request.url_root.rstrip("/") + f"/send/{key}"
    logger.info("API generated link %s for admin %s", link, admin_id)
    return jsonify({"status":"success","generated_link":link})

@app.route("/send/<key>", methods=["GET", "POST"])
def send_page(key):
    if key not in BOT_LINKS:
        logger.warning("Invalid send key used: %s", key)
        return "<h3 style='color:red;text-align:center'>Invalid or expired link ❌</h3>", 404

    creds = BOT_LINKS[key]
    message = None
    if request.method == "POST":
        msg1 = (request.form.get("msg1") or "").strip()
        msg2 = (request.form.get("msg2") or "").strip()
        logger.info("Send request for key=%s admin=%s", key, creds.get("admin"))
        ok1 = False
        ok2 = False
        try:
            ok1 = send_message_to_admin(creds["token"], creds["admin"], msg1)
        except Exception as e:
            logger.exception("Error sending msg1: %s", e)
        try:
            ok2 = send_message_to_admin(creds["token"], creds["admin"], msg2)
        except Exception as e:
            logger.exception("Error sending msg2: %s", e)

        if ok1 and ok2:
            message = "✅ Both messages sent successfully!"
        elif ok1 or ok2:
            message = "⚠️ One message sent; one failed."
        else:
            message = "❌ Failed to send messages. Check bot token and admin id in logs."

    return render_template_string(SEND_HTML, message=message)

# A simple health check for Render and uptime monitors
@app.route("/health")
def health():
    return jsonify({"status":"ok"}), 200

# Friendly error handler to ensure 500s show logs in Render
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    return jsonify({"status":"error","message":"Internal server error"}), 500

if __name__ == "__main__":
    # Render provides a PORT env var; fallback to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting app on port %s", port)
    app.run(host="0.0.0.0", port=port)
