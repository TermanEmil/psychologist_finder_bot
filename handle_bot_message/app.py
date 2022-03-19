import json

import telegram

from SubmittedForm import get_all_submitted_forms
from message_handlers.main import handle_message
from telegram_bot import get_bot


def lambda_handler(event, context):
    update = telegram.Update.de_json(json.loads(event['body']), get_bot())
    handle_message(update)

    return {"statusCode": 204}


def lambda_handler_get_submitted_forms(event, context):
    forms = get_all_submitted_forms()

    response_body = {
        'forms': forms
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }
