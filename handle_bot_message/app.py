import asyncio
import json
import os
import sys

from telegram import Update, Bot

from consts import patient_type
from query_utils import extract_query_params


def get_bot_token(context) -> str:
    if ':Prod' in context.invoked_function_arn:
        environment = ''
    else:
        environment = 'DEV'

    return os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")


async def handle_async(event, context):
    from message_handlers.main import handle_message

    try:
        async with Bot(token=get_bot_token(context)) as bot:
            update = Update.de_json(json.loads(event['body']), bot)
            await handle_message(update, None)
    except Exception as e:
        print(e, file=sys.stderr)
        return {"statusCode": 500}

    return {"statusCode": 204}


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(handle_async(event, context))


def extract_event_query_params(event):
    if 'queryStringParameters' in event:
        return extract_query_params(event['queryStringParameters'])
    else:
        return extract_query_params({})


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_paginated_submitted_forms

    # print('event:', json.dumps(event))
    page_size, starting_token, person_type = extract_event_query_params(event)
    result = get_paginated_submitted_forms(starting_token, page_size, person_type)
    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False).encode('utf8')
    }
