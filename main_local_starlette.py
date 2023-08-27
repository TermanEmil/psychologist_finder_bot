import asyncio
import json
import os
from dataclasses import asdict

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from src.SubmittedForm import get_all_submitted_forms
from src.update_handler import setup_webhook, handle_bot_request


async def main() -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = os.environ.get("NGROK_WEBSERVER_URL")
    await setup_webhook(bot_token=bot_token, url=f"{url}/telegram")

    async def telegram_endpoint(request: Request) -> Response:
        message = await request.json()
        await handle_bot_request(bot_token, message)
        return Response()

    # async def get_all_endpoint(request: Request) -> Response:
    #     forms = [asdict(form) for form in get_all_submitted_forms()]
    #     return Response(json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8'), media_type='application/json')

    webserver = uvicorn.Server(
        config=uvicorn.Config(
            port=5000,
            use_colors=False,
            host="127.0.0.1",
            app=Starlette(
                routes=[
                    Route("/telegram", telegram_endpoint, methods=["POST"]),
                    # Route("/all", get_all_endpoint, methods=["GET"]),
                ],
                middleware=[
                    Middleware(CORSMiddleware, allow_origins=['*'])
                ],
            ),
        )
    )

    # Run application and webserver together
    await webserver.serve()


if __name__ == "__main__":
    asyncio.run(main())
