import asyncio
import json
import os
import sys

from telegram import Update, Bot


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


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_paginated_submitted_forms

    # print('event:', json.dumps(event))
    query = event['queryStringParameters']
    page_size_key = 'pageSize'
    if page_size_key in query and query[page_size_key].isdecimal():
        page_size = int(query[page_size_key])
    else:
        page_size = 50

    if 'startingToken' in query:
        starting_token = query['startingToken']
    else:
        starting_token = None

    result = get_paginated_submitted_forms(starting_token, page_size)
    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False).encode('utf8')
    }
