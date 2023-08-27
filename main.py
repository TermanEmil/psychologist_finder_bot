import asyncio
import json
import os
from dataclasses import asdict

import functions_framework

@functions_framework.http
def bot_update_handler(request):
    request_json = request.get_json(silent=True)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise

    async def handle_async(request):
        from src.update_handler import handle_bot_request

        await handle_bot_request(os.environ.get(f"TELEGRAM_BOT_TOKEN"), request)
        return {"statusCode": 200}

    return loop.run_until_complete(handle_async(request_json))


@functions_framework.http
def get_all_submissions_handler(request):
    request_json = request.get_json(silent=True)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise


    async def handle_async(request):
        from src.SubmittedForm import get_all_submitted_forms

        forms = [asdict(form) for form in get_all_submitted_forms()]
        return {
            'statusCode': 200,
            'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
        }

    return loop.run_until_complete(handle_async(request_json))
