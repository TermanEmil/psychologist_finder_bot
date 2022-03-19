import uuid
from dataclasses import dataclass, asdict
from datetime import datetime

import pytz

import configs
from aws import get_db, get_db_client


@dataclass
class SubmittedForm:
    chat_id: int
    person_type: str
    name: str
    age: int
    contact_means: str
    contact: str

    id: str = str(uuid.uuid4())
    submission_time: str = datetime.now(tz=pytz.UTC).isoformat()


def _get_submissions_table():
    return get_db().Table(configs.submitted_forms_table_name)


def save_submission(submission: SubmittedForm):
    _get_submissions_table().put_item(Item=asdict(submission))


def get_all_submitted_forms():
    paginator = get_db_client().get_paginator('scan')
    iterator = paginator.paginate(TableName=configs.submitted_forms_table_name)
    return list(iterator)
