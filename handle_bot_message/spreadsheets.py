import base64
import os
from datetime import datetime

import gspread
import pytz

from SubmittedForm import SubmittedForm


def add_to_spreadsheet(form: SubmittedForm):
    print(f"Adding to spreadsheets for chat_id: {form.chat_id}")

    base64_private_key = os.getenv('GSPREAD_PRIVATE_KEY').encode('utf-8')
    private_key = base64.decodebytes(base64_private_key).decode('utf-8')

    credentials = {
        "type": "service_account",
        "project_id": "psychologist-finder-bot",
        "private_key_id": os.getenv('GSPREAD_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.getenv('GSPREAD_CLIENT_EMAIL'),
        "client_id": os.getenv('GSPREAD_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('GSPREAD_CLIENT_X509_CERT_URL')
    }

    gc = gspread.service_account_from_dict(credentials)
    submissions = gc.open_by_key(os.environ.get('GSPREAD_SPREADSHEET_ID')).sheet1
    submission_time = datetime.fromisoformat(form.submission_time)

    submissions.append_row([
        form.person_type,
        form.name,
        form.age,
        form.contact_means,
        form.contact,
        submission_time.astimezone(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S, %m/%d/%Y'),
    ])
    print(f"Added to spreadsheets for chat_id: {form.chat_id}")
