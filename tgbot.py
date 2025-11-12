import requests

def send_message_to_admin(bot_token, admin_id, message):
    """Send message to Telegram Admin"""
    try:
        if not message:
            return False
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": admin_id, "text": message}
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print("Error:", e)
        return False
