import asyncio
import json
import os
from dataclasses import asdict

from telegram import Update, Bot


def get_bot_token(context) -> str:
    if ':Prod' in context.invoked_function_arn:
        environment = ''
    else:
        environment = 'DEV'

    return os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")


def lambda_handler(event, context):
    from message_handlers.main import handle_message

    try:
        with Bot(token=get_bot_token(context)) as bot:
            update = Update.de_json(json.loads(event['body']), bot)
            asyncio.get_event_loop().run_until_complete(handle_message(update, None))
    except Exception as e:
        print(e)
        return {"statusCode": 500}

    return {"statusCode": 204}


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_all_submitted_forms

    forms = [asdict(form) for form in get_all_submitted_forms()]
    return {
        'statusCode': 200,
        'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
    }
