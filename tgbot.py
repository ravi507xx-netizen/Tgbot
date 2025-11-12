import requests

def send_message_to_admin(bot_token, admin_id, message):
    """Send a custom message to the Telegram Admin"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": admin_id, "text": message}
        r = requests.post(url, data=data)
        return r.status_code == 200
    except Exception as e:
        print("Error sending:", e)
        return False
