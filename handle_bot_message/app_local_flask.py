import flask
from flask import request


app = flask.Flask(__name__)


@app.post("/handle_bot_message")
def handle_bot_message():
    if flask.request.headers.get('content-type') == 'application/json':
        bot_message = request.json['message']
        print(bot_message)

    return '', 204
