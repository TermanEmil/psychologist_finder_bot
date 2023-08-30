from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from src.auxiliary.bot_utils import stringify
from src.auxiliary.logger import logger
from src.auxiliary.stopwatch import Stopwatch
from src.message_handlers.main import handle_message

JSONDict = Dict[str, Any]


def _extract_user_id(message_data: dict) -> Optional[int]:
    if message_data is None:
        return None

    if 'message' in message_data:
        key = 'message'
    elif 'inline_query' in message_data:
        key = 'inline_query'
    elif 'callback_query' in message_data:
        key = 'callback_query'
    else:
        return None

    return message_data[key]['from']['id']


async def handle_bot_request(bot_token: str, message_data: dict):
    user_id = _extract_user_id(message_data)
    if user_id is None:
        return

    logger.info(f'Handling bot request for user {user_id}')

    application = Application.builder() \
        .token(bot_token) \
        .build()

    application.add_handler(MessageHandler(filters.ALL, handle_message))

    with Stopwatch(name='application.process_update()'):
        try:
            async with application:
                update = Update.de_json(data=message_data, bot=application.bot)
                logger.info(f'Processing request: {stringify(update)}.')
                await application.process_update(update)
                logger.info(f'User {user_id}: Request handling finished.')
        except Exception as e:
            raise Exception(f'User {user_id}: Request handling failed.') from e


async def setup_webhook(bot_token: str, url: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.set_webhook(url=url)
