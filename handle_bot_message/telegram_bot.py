import os

import telegram


_bot = telegram.Bot(os.environ.get("TELEGRAM_BOT_TOKEN"))


def get_bot() -> telegram.Bot:
    return _bot
