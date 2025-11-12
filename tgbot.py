# tgbot.py
import requests
import logging

logger = logging.getLogger(__name__)

def send_message_to_admin(bot_token: str, admin_id: str, message: str) -> bool:
    """
    Send a text message to the given admin_id via the provided bot_token.
    Returns True on HTTP 200 success, otherwise False.
    """
    try:
        if not bot_token or not admin_id or not message:
            logger.error("Missing token/admin/message")
            return False
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": admin_id, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        logger.info("Telegram sendMessage response: status=%s body=%s", r.status_code, r.text)
        return r.status_code == 200
    except requests.RequestException as e:
        logger.exception("RequestException while sending message: %s", e)
        return False
    except Exception as e:
        logger.exception("Unexpected error in send_message_to_admin: %s", e)
        return False
