import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


DB_NAME = 'psychologist-finder-bot'
CONVERSATIONS_NAME = 'conversations'
USER_DATA_NAME = 'user_data'
FORM_DATA_NAME = 'form_data'
SUBMITTED_FORM_DATA_NAME = 'submitted_form_data'


def get_db_client() -> MongoClient:
    # Create a new client and connect to the server
    uri = os.environ.get('MONGO_DB_URI')
    return MongoClient(uri, server_api=ServerApi('1'))


