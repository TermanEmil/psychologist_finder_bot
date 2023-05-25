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


def extract_query_params(event):
    page_size = 50
    starting_token = None

    if 'queryStringParameters' in event:
        query = event['queryStringParameters']
        page_size_key = 'pageSize'
        if page_size_key in query and query[page_size_key].isdecimal():
            raw_page_size = int(query[page_size_key])
            if raw_page_size > 0 and page_size <= 5000:
                page_size = raw_page_size

        starting_token_key = 'startingToken'
        if starting_token_key in query and query[starting_token_key]:
            starting_token = query['startingToken']

    return page_size, starting_token


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_paginated_submitted_forms

    # print('event:', json.dumps(event))
    page_size, starting_token = extract_query_params(event)
    result = get_paginated_submitted_forms(starting_token, page_size)
    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False).encode('utf8')
    }
