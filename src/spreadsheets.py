import base64
import json
import os
from datetime import datetime

import gspread
import pytz

from src.SubmittedForm import SubmittedForm, get_all_submitted_forms


def _get_spreadsheet_configs():
    return json.loads(os.getenv('GOOGLE_SPREADSHEETS').encode('utf-8'))


def build_gspread_client() -> gspread.Client:
    spreadsheets_config = _get_spreadsheet_configs()
    base64_private_key = bytes(spreadsheets_config['GSPREAD_PRIVATE_KEY'], 'utf-8')
    private_key = base64.decodebytes(base64_private_key).decode('utf-8')

    credentials = {
        "type": "service_account",
        "project_id": "psychologist-finder-bot",
        "private_key_id": spreadsheets_config['GSPREAD_PRIVATE_KEY_ID'],
        "private_key": private_key,
        "client_email": spreadsheets_config['GSPREAD_CLIENT_EMAIL'],
        "client_id": spreadsheets_config['GSPREAD_CLIENT_ID'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": spreadsheets_config['GSPREAD_CLIENT_X509_CERT_URL']
    }

    return gspread.service_account_from_dict(credentials)


_client = build_gspread_client()


def add_to_spreadsheet(form: SubmittedForm):
    print(f"Adding to spreadsheets for chat_id: {form.chat_id}")
    submissions = _client.open_by_key(_get_spreadsheet_configs()['GSPREAD_SPREADSHEET_ID']).sheet1
    submissions.append_row(_build_row(form))
    print(f"Added to spreadsheets for chat_id: {form.chat_id}")


def add_all_forms_to_spreadsheets():
    submissions = _client.open_by_key(_get_spreadsheet_configs()['GSPREAD_SPREADSHEET_ID']).sheet1
    submissions.append_rows(list(_build_rows_for_all_submitted_forms()))


def _build_rows_for_all_submitted_forms():
    forms = sorted(
        get_all_submitted_forms(),
        key=lambda x: datetime.fromisoformat(x['submission_time']).astimezone(pytz.timezone('Europe/Kiev')))

    for form in forms:
        yield _build_row(form)


def _build_row(form: SubmittedForm):
    submission_time = datetime.fromisoformat(form.submission_time)
    return [
        form.person_type,
        form.name,
        form.age,
        form.contact_means,
        form.contact,
        form.consultation_preference,
        submission_time.astimezone(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S, %d/%m/%Y'),
    ]