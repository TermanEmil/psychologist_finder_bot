import flask
import telegram
from flask import request

from message_handlers.main import handle_message
from telegram_bot import get_bot

app = flask.Flask(__name__)


@app.post("/handle_bot_message")
def handle_bot_message():
    if flask.request.headers.get('content-type') == 'application/json':
        update = telegram.Update.de_json(request.get_json(force=True), get_bot())
        handle_message(update)

    return '', 204
