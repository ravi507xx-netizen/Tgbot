import requests

def send_hi_to_admin(bot_token, admin_id):
    """Send 'Hi 👋' message to the Telegram Admin"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": admin_id,
            "text": "Hi 👋 from your bot!"
        }
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print("Error:", e)
        return False
