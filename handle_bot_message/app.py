import json


def lambda_handler(event, context):
    message = json.loads(event['body'])
    if 'message' in message:
        bot_message = message['message']

    return {"statusCode": 204}

