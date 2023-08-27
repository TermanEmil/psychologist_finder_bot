from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

import pytz

from src.auxiliary import db
from src.auxiliary.stopwatch import Stopwatch


@dataclass
class Form:
    chat_id: int
    stage: int = 0

    person_type: str = None
    name: str = None
    age: int = None
    contact_means: str = None
    contact: str = None
    consultation_preference: str = None
    last_updated: str = datetime.now(tz=pytz.UTC).isoformat()


def update_form(form: Form):
    form.last_updated = datetime.now(tz=pytz.UTC).isoformat()
    with Stopwatch('update_form'):
        with db.get_db_client() as client:
            client[db.DB_NAME][db.FORM_DATA_NAME].update_one(
                {'chat_id': form.chat_id},
                {"$set": asdict(form)},
                upsert=True
            )


def find_form(chat_id: int) -> Optional[Form]:
    with Stopwatch('find_form'):
        with db.get_db_client() as client:
            item = client[db.DB_NAME][db.FORM_DATA_NAME].find_one({'chat_id': chat_id})

    if item is None:
        return None

    cleaned_data = {key: item[key] for key in item.keys() if key not in ['_id']}
    form = Form(**cleaned_data)
    return form


def delete_form(form: Form):
    with Stopwatch('delete_form'):
        with db.get_db_client() as client:
            client[db.DB_NAME][db.FORM_DATA_NAME].delete_one({'chat_id': form.chat_id})
