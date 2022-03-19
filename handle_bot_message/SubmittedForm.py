import uuid
from dataclasses import dataclass, asdict
from datetime import datetime

import pytz

import configs
from aws import get_db


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


def save_submission(submission: SubmittedForm):
    table = get_db().Table(configs.submitted_forms_table_name)
    table.put_item(Item=asdict(submission))
