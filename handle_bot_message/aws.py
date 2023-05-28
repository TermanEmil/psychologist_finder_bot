import os

import boto3
from botocore.client import BaseClient

import migrations


dynamodb = boto3.resource(
    'dynamodb',
    region_name='eu-central-1',
    aws_access_key_id=os.environ.get('CONFIG_AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('CONFIG_AWS_SECRET_ACCESS_KEY'))


def get_db():
    # migrations.ensure_forms_table_exists(dynamodb)
    # migrations.ensure_submitted_forms_table_exists(dynamodb)
    return dynamodb


def get_db_client() -> BaseClient:
    return boto3.client(
        'dynamodb',
        region_name='eu-central-1',
        aws_access_key_id=os.environ.get('CONFIG_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('CONFIG_AWS_SECRET_ACCESS_KEY'))
