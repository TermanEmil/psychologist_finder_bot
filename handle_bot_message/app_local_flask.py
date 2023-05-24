import asyncio
import logging
import os

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters, ConversationHandler, MessageHandler
)

from Form import update_form, Form
from message_handlers.main import handle_message

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class Steps:
    WHO, NAME = range(2)


patient_type = 'Мешканець/ка мiста'
psychologist_type = 'Психолог'
person_types = [patient_type, psychologist_type]

who_are_you = 'Хто ви?'

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update_form(Form(chat_id=update.message.chat_id))
    markup = ReplyKeyboardMarkup([person_types], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(text=who_are_you, reply_markup=markup)
    return Steps.WHO


async def all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await handle_message(update)


async def who_am_i_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    person_type = update.message.text
    await update.message.reply_text(f"You are: {person_type}")
    return Steps.NAME


who_am_i_filter = filters.Regex(f"^({patient_type}|{psychologist_type})$")


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


async def main() -> None:
    """Set up the application and a custom webserver."""
    url = "https://d15b-2a01-cb15-330-e00-2990-7496-701-a6c2.ngrok-free.app"
    admin_chat_id = 123456
    port = 5000

    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (
        Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).updater(None).build()
    )
    # save the values in `bot_data` such that we may easily access them in the callbacks
    application.bot_data["url"] = url
    application.bot_data["admin_chat_id"] = admin_chat_id

    # register handlers
    application.add_handler(MessageHandler(filters.ALL, all_handler))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{url}/telegram")

    # Set up webserver
    async def telegram(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=port,
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