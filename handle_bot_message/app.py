import json

import telegram

from message_handlers.main import handle_message
from telegram_bot import get_bot


def lambda_handler(event, context):
    update = telegram.Update.de_json(json.loads(event['body']), get_bot())
    handle_message(update)

    return {"statusCode": 204}
