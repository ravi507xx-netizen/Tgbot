from flask import Flask, render_template_string, request
from tgbot import send_hi_to_admin

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Bot Sender</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
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
        button:hover {
            background-color: #009624;
        }
    </style>
</head>
<body>
    <h1>Send "Hi 👋" to Admin via Telegram Bot</h1>
    <form method="POST">
        <input type="text" name="bot_token" placeholder="Enter Your Bot Token" required><br>
        <input type="text" name="admin_id" placeholder="Enter Telegram Admin ID" required><br>
        <button type="submit">Send Hi</button>
    </form>
    {% if message %}
        <h3>{{ message }}</h3>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        bot_token = request.form["bot_token"]
        admin_id = request.form["admin_id"]
        success = send_hi_to_admin(bot_token, admin_id)
        if success:
            message = "✅ Message sent successfully!"
        else:
            message = "❌ Failed to send message. Please check token or ID."
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
