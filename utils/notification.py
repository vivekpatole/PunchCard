import logging

import requests

logger = logging.getLogger(__name__)


def send_telegram_message(api_token, chat_id, message):
    api_url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    try:
        response = requests.post(api_url, json={'chat_id': chat_id, 'text': message})
        logger.info(f'Telegram Response: {response.text}')
    except Exception as e:
        logger.error(f'Error while sending telegram message: {e}')
