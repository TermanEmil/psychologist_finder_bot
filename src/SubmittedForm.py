import math
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

import pytz
from bson import ObjectId

from src.auxiliary import db
from src.auxiliary.stopwatch import Stopwatch


@dataclass
class SubmittedForm:
    chat_id: int
    person_type: str
    name: str
    age: int
    contact_means: str
    contact: str

    consultation_preference: Optional[str] = None
    _id: Optional[ObjectId] = None

    submission_time: str = datetime.now(tz=pytz.UTC).isoformat()


def save_submission(submission: SubmittedForm):
    with Stopwatch('save_submission'):
        with db.get_db_client() as client:
            client[db.DB_NAME][db.SUBMITTED_FORM_DATA_NAME].insert_one(asdict(submission))


def get_all_submitted_forms():
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.SUBMITTED_FORM_DATA_NAME].find({})

        for item in items:
            for k, v in item.items():
                if type(item[k]) == float and math.isnan(item[k]):
                    item[k] = ''

            yield {
                'id': str(item['_id']),
                'person_type': item['person_type'],
                'name': item['name'],
                'age': item['age'],
                'contact_means': item['contact_means'],
                'contact': item['contact'],
                'consultation_preference': item['consultation_preference'],
                'submission_time': item['submission_time']
            }


def any_key(some_dict: dict):
    if some_dict is None:
        return None

    return list(some_dict.values())[0]
