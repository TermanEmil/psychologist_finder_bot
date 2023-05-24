import asyncio
import json
import os
from dataclasses import asdict

from telegram import Update
from telegram.ext import Application, MessageHandler, filters


_application = None

def get_application(context) -> Application:
    global _application

    if _application is None:
        print('Acquiring Telegram Bot connection')

        if ':Prod' in context.invoked_function_arn:
            environment = ''
        else:
            environment = 'DEV'

        bot_token = os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")
        _application = Application.builder().token(bot_token).build()
        print('Finished acquiring Telegram Bot connection')

    return _application

def lambda_handler(event, context):
    from message_handlers.main import handle_message

    print('Starting handling')
    # application = get_application(context)
    # application.add_handler(MessageHandler(filters.ALL, handle_message))
    #
    # try:
    #     update = Update.de_json(json.loads(event['body']), application.bot)
    #     asyncio.get_event_loop().run_until_complete(application.process_update(update))
    # except Exception as e:
    #     print(e)
    #     return {"statusCode": 500}

    return {"statusCode": 204}


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_all_submitted_forms

    forms = [asdict(form) for form in get_all_submitted_forms()]
    return {
        'statusCode': 200,
        'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
    }
