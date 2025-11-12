from flask import Flask, render_template_string, request, jsonify
from tgbot import send_message_to_admin
import random, string, os

app = Flask(__name__)

# Store links temporarily in memory
BOT_LINKS = {}

# =================== HTML Templates ===================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Link Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            text-align: center;
            padding-top: 80px;
        }
        form {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            display: inline-block;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        input {
            width: 300px;
            padding: 10px;
            margin: 10px;
            border: none;
            border-radius: 10px;
        }
        button {
            padding: 10px 25px;
            border: none;
            border-radius: 10px;
            background-color: #00c853;
            color: white;
            cursor: pointer;
        }
        button:hover { background-color: #009624; }
        .link-box {
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            padding: 10px;
            margin-top: 20px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <h1>Generate Telegram Message Link</h1>
    <form method="POST">
        <input type="text" name="admin_id" placeholder="Enter Admin ID" required><br>
        <input type="text" name="bot_token" placeholder="Enter Bot Token" required><br>
        <button type="submit">Generate Link</button>
    </form>
    {% if link %}
    <div class="link-box">
        <h3>Your Link:</h3>
        <a href="{{ link }}" target="_blank" style="color:#00e676;">{{ link }}</a>
    </div>
    {% endif %}
</body>
</html>
"""

SEND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Send Message</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #141E30, #243B55);
            color: white;
            text-align: center;
            padding-top: 80px;
        }
        form {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            display: inline-block;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        textarea {
            width: 300px;
            height: 80px;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            border: none;
            resize: none;
        }
        button {
            padding: 10px 25px;
            border: none;
            border-radius: 10px;
            background-color: #00c853;
            color: white;
            cursor: pointer;
        }
        button:hover { background-color: #009624; }
    </style>
</head>
<body>
    <h1>Send Messages to Admin</h1>
    <form method="POST">
        <textarea name="msg1" placeholder="Enter Message 1..." required></textarea><br>
        <textarea name="msg2" placeholder="Enter Message 2..." required></textarea><br>
        <button type="submit">Send Both Messages</button>
    </form>
    {% if message %}
        <h3>{{ message }}</h3>
    {% endif %}
</body>
</html>
"""

# =================== ROUTES ===================

@app.route("/", methods=["GET", "POST"])
def home():
    """Home page to enter Bot Token + Admin ID"""
    link = None
    if request.method == "POST":
        admin_id = request.form.get("admin_id").strip()
        bot_token = request.form.get("bot_token").strip()
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        BOT_LINKS[key] = {"admin": admin_id, "token": bot_token}
        link = request.url_root.strip("/") + f"/send/{key}"
    return render_template_string(HOME_HTML, link=link)


@app.route("/link/admin<admin_id>&token<bot_token>", methods=["GET"])
def api_generate_link(admin_id, bot_token):
    """API: /link/admin{admin_id}&token{bot_token}"""
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    BOT_LINKS[key] = {"admin": admin_id, "token": bot_token}
    link = request.url_root.strip("/") + f"/send/{key}"
    return jsonify({"status": "success", "generated_link": link})


@app.route("/send/<key>", methods=["GET", "POST"])
def send_page(key):
    """Page for sending Message 1 and 2"""
    if key not in BOT_LINKS:
        return "<h3 style='color:red;text-align:center'>Invalid or expired link ❌</h3>"

    creds = BOT_LINKS[key]
    message = None

    if request.method == "POST":
        msg1 = request.form.get("msg1")
        msg2 = request.form.get("msg2")

        ok1 = send_message_to_admin(creds["token"], creds["admin"], msg1)
        ok2 = send_message_to_admin(creds["token"], creds["admin"], msg2)

        message = "✅ Both messages sent successfully!" if ok1 and ok2 else "❌ Failed to send messages."

    return render_template_string(SEND_HTML, message=message)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render assigns its own port
    app.run(host="0.0.0.0", port=port)
