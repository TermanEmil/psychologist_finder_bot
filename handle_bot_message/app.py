import json
from dataclasses import asdict


def lambda_handler(event, context):
    import telegram
    from telegram_bot import get_bot
    from message_handlers.main import handle_message

    update = telegram.Update.de_json(json.loads(event['body']), get_bot())
    handle_message(update)

    return {"statusCode": 204}


def lambda_handler_get_submitted_forms(event, context):
    from SubmittedForm import get_all_submitted_forms

    forms = [asdict(form) for form in get_all_submitted_forms()]
    return {
        'statusCode': 200,
        'body': json.dumps({'forms': forms}, ensure_ascii=False).encode('utf8')
    }
