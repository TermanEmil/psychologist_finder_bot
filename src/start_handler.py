from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = '\n'.join([
        'Привіт'
    ])

    await update.message.reply_text(text)
