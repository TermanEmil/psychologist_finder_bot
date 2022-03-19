import sys

import telegram
from werkzeug.exceptions import Unauthorized, BadRequest


def handle_message(update: telegram.Update):
    try:
        handle_core(update)
    except Unauthorized as e:
        print(f"Unauthorized: {e}", file=sys.stderr)
    except BadRequest as e:
        print(f"Bad request: {e}", file=sys.stderr)


def handle_core(update: telegram.Update):
    if update.message.from_user.is_bot:
        return

