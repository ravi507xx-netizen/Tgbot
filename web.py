from flask import Flask, render_template_string, request
from tgbot import send_message_to_admin
import random, string

app = Flask(__name__)

# Store generated links temporarily (in memory)
BOT_LINKS = {}

# HTML Template for message sending page
SEND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Send Message to Admin</title>
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
        input, textarea {
            width: 300px;
            padding: 10px;
            margin: 10px;
            border-radius: 10px;
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
        button:hover {
            background-color: #009624;
        }
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

@app.route("/link/<path:info>")
def generate_link(info):
    """
    API Endpoint:
    Example: /link/{admin_id}{bot_token}
    Generates a unique message-sending link
    """
    # Separate admin_id and bot_token by assuming admin_id is numeric
    admin_id = ''.join([c for c in info if c.isdigit()])
    bot_token = info.replace(admin_id, '')

    # Generate random 8-char key
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    BOT_LINKS[key] = {"admin": admin_id, "token": bot_token}

    full_link = request.url_root.strip("/") + f"/send/{key}"
    return {
        "status": "success",
        "message": "Link generated successfully!",
        "generated_link": full_link
    }

@app.route("/send/<key>", methods=["GET", "POST"])
def send_page(key):
    if key not in BOT_LINKS:
        return "<h3 style='color:red;text-align:center'>Invalid or expired link ❌</h3>"

    creds = BOT_LINKS[key]
    message = None

    if request.method == "POST":
        msg1 = request.form.get("msg1")
        msg2 = request.form.get("msg2")

        ok1 = send_message_to_admin(creds["token"], creds["admin"], msg1)
        ok2 = send_message_to_admin(creds["token"], creds["admin"], msg2)

        if ok1 and ok2:
            message = "✅ Both messages sent successfully!"
        else:
            message = "❌ Failed to send one or both messages."

    return render_template_string(SEND_HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    link = None
    if request.method == "POST":
        bot_token = request.form["bot_token"].strip()
        admin_id = request.form["admin_id"].strip()

        # Generate random unique key
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        BOT_DATA[key] = {"token": bot_token, "admin": admin_id}

        link = request.url_root.strip("/") + url_for("send_page", unique_id=key)
    return render_template_string(HOME_HTML, link=link)

@app.route("/send/<unique_id>", methods=["GET", "POST"])
def send_page(unique_id):
    if unique_id not in BOT_DATA:
        return "<h3 style='color:red;text-align:center'>Invalid or expired link ❌</h3>"

    message = None
    creds = BOT_DATA[unique_id]

    if request.method == "POST":
        user_msg = request.form["message"]
        success = send_message_to_admin(creds["token"], creds["admin"], user_msg)
        message = "✅ Message sent successfully!" if success else "❌ Failed to send."

    return render_template_string(SEND_HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
