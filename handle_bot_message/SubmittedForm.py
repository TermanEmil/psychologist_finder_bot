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

    consultation_preference: str = None

    id: str = str(uuid.uuid4())
    submission_time: str = datetime.now(tz=pytz.UTC).isoformat()


def _get_submissions_table():
    return get_db().Table(configs.submitted_forms_table_name)


def save_submission(submission: SubmittedForm):
    _get_submissions_table().put_item(Item=asdict(submission))


def get_all_submitted_forms():
    paginator = get_db_client().get_paginator('scan')
    iterator = paginator.paginate(TableName=configs.submitted_forms_table_name)

    for page in iterator:
        for item in page['Items']:
            yield SubmittedForm(
                chat_id=any_key(item['chat_id']),
                person_type=any_key(item['person_type']),
                name=any_key(item['name']),
                age=any_key(item['age']),
                contact_means=any_key(item['contact_means']),
                contact=any_key(item['contact']),
                consultation_preference=any_key(item.get('consultation_preference')),
                id=any_key(item['id']),
                submission_time=any_key(item['submission_time']))


def get_paginated_submitted_forms(starting_token: str, page_size: int):
    paginator = get_db_client().get_paginator('scan').paginate(
        TableName=configs.submitted_forms_table_name,
        PaginationConfig={
            "PageSize": page_size,
            "MaxItems": page_size,
            "StartingToken": starting_token
        }
    )

    return paginator.build_full_result()


def any_key(some_dict: dict):
    if some_dict is None:
        return None

    return list(some_dict.values())[0]
