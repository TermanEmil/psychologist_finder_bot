import json
import os
import sys
from dataclasses import asdict

from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(token=bot_token)

application = Application.builder().token(bot_token).build()


async def lambda_handler(event, context):
    from message_handlers.main import handle_message

    application.add_handler(MessageHandler(filters.ALL, handle_message))

    update = Update.de_json(json.loads(event['body']), bot)
    await application.process_update(update)

    return {"statusCode": 204}


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_all_submitted_forms

    forms = [asdict(form) for form in get_all_submitted_forms()]
    return {
        'statusCode': 200,
        'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
    }
