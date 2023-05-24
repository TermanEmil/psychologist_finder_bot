# import json
import logging
import os
# import sys
# from dataclasses import asdict
#
# from telegram import Update
from telegram.ext import Application, MessageHandler, filters


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


_application = None

def get_application(context) -> Application:
    global _application

    if _application is None:
        if ':Dev' in context.invoked_function_arn:
            environment = 'DEV'
        else:
            environment = ''

        bot_token = os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")
        _application = Application.builder().token(bot_token).build()

    return _application

def lambda_handler(event, context):
    return "Hello world"


def lambda_handler_get_submitted_forms(event, context):
    # from SubmittedForm import get_all_submitted_forms

    # forms = [asdict(form) for form in get_all_submitted_forms()]
    return {
        'statusCode': 200,
        # 'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
    }
