from flask import Flask, render_template_string, request, redirect, url_for
from tgbot import send_message_to_admin
import random, string

app = Flask(__name__)

# Temporary storage for bot credentials
BOT_DATA = {}

# HTML templates
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bot Link Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #141E30, #243B55);
            color: white;
            text-align: center;
            padding-top: 100px;
        }
        form {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            display: inline-block;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        input {
            padding: 10px;
            margin: 10px;
            border: none;
            border-radius: 10px;
            width: 250px;
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
    <h1>Generate Telegram Message Sender Link</h1>
    <form method="POST">
        <input type="text" name="bot_token" placeholder="Enter Bot Token" required><br>
        <input type="text" name="admin_id" placeholder="Enter Admin ID" required><br>
        <button type="submit">Generate Link</button>
    </form>
    {% if link %}
        <h3>Your Unique Link:</h3>
        <p><a href="{{ link }}" target="_blank" style="color: #00e676;">{{ link }}</a></p>
    {% endif %}
</body>
</html>
"""

SEND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Send Message to Admin</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
            color: white;
            text-align: center;
            padding-top: 100px;
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
            height: 100px;
            border-radius: 10px;
            padding: 10px;
            border: none;
            resize: none;
        }
        button {
            margin-top: 10px;
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
    <h1>Send Message to Admin</h1>
    <form method="POST">
        <textarea name="message" placeholder="Enter your message..." required></textarea><br>
        <button type="submit">Send Message</button>
    </form>
    {% if message %}
        <h3>{{ message }}</h3>
    {% endif %}
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
