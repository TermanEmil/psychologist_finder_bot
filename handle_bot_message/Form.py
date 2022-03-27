from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Any

import pytz

import configs
from aws import get_db


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


_forms_table: Any = None


def get_forms_table():
    global _forms_table

    if _forms_table is None:
        _forms_table = get_db().Table(configs.forms_table_name)
    return _forms_table


def update_form(form: Form):
    form.last_updated = datetime.now(tz=pytz.UTC).isoformat()
    get_forms_table().put_item(Item=asdict(form))


def find_form(chat_id: int) -> Optional[Form]:
    item = get_forms_table().get_item(Key={'chat_id': chat_id})

    if 'Item' not in item:
        return None

    form = Form(**item['Item'])
    form.chat_id = int(form.chat_id)
    return form


def delete_form(form: Form):
    get_forms_table().delete_item(Key={'chat_id': form.chat_id})
