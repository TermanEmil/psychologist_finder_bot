from typing import TypedDict

from auxiliary import db
from auxiliary.stopwatch import Stopwatch


class UserData(TypedDict):
    user_id: int
    data: dict


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if len(data) > 0:
        user_data = UserData(user_id=user_id, data=data)

        with Stopwatch('update_or_create_user_data'):
            with db.get_db_client() as client:
                client[db.DB_NAME][db.USER_DATA_NAME].update_one(
                    {'user_id': user_id},
                    {"$set": user_data}, upsert=True
                )


def get_user_data(user_id: int) -> dict:
    with Stopwatch('get_user_data'):
        with db.get_db_client() as client:
            item = client[db.DB_NAME][db.USER_DATA_NAME].find_one({'user_id': user_id})

    if item is None:
        data = {}
    else:
        data = item['data']

    return data
