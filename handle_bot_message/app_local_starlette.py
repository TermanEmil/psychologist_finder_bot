import asyncio
import json
import logging
import os

import uvicorn
from starlette.applications import Starlette
from starlette.datastructures import QueryParams
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import (
    Application,
    filters, MessageHandler
)

from SubmittedForm import get_paginated_submitted_forms
from consts import patient_type, person_types_keys
from message_handlers.main import handle_message
from query_utils import extract_query_params

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Set up the application and a custom webserver."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = os.environ.get("NGROK_WEBSERVER_URL")

    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (Application.builder().token(bot_token).updater(None).build())

    # register handlers
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{url}/telegram")

    # Set up webserver
    async def telegram_endpoint(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    async def get_submitted_forms_endpoint(request: Request) -> Response:
        page_size, starting_token, person_type = extract_query_params(dict(request.query_params))
        result = get_paginated_submitted_forms(starting_token, page_size, person_type)
        body = json.dumps(result, ensure_ascii=False).encode('utf8')
        return Response(status_code=200, content=body)

    middleware = [
        Middleware(CORSMiddleware, allow_origins=['*'])
    ]

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram_endpoint, methods=["POST"]),
            Route("/submitted_forms", get_submitted_forms_endpoint, methods=["GET"])
        ],
        middleware=middleware
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=5000,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())