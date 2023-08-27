import uuid
from dataclasses import dataclass, asdict
from datetime import datetime

import pytz

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

    consultation_preference: str = None

    submission_time: str = datetime.now(tz=pytz.UTC).isoformat()
    id: str = str(uuid.uuid4())


def save_submission(submission: SubmittedForm):
    with Stopwatch('save_submission'):
        with db.get_db_client() as client:
            client[db.DB_NAME][db.SUBMITTED_FORM_DATA_NAME].insert_one(asdict(submission))


def get_all_submitted_forms():
    with Stopwatch('save_submission'):
        with db.get_db_client() as client:
            items = client[db.DB_NAME][db.SUBMITTED_FORM_DATA_NAME].find({})
            for item in items:
                item.pop('_id')
                yield SubmittedForm(**item)


def any_key(some_dict: dict):
    if some_dict is None:
        return None

    return list(some_dict.values())[0]
