""" Main code package """

from typing import Any, Dict
import json
import logging
import base64
import os
from cerberus import Validator
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CustomValidator(Validator):
    '''
    Simple utility to encapsulate a schema validate with Cerberus (which has to be on the PYTHONPATH)
    '''

    def __init__(self, schema):
        super().__init__(schema)
        self.purge_unknown = True

    def validate_event(self, the_input):
        ''' Validate the value passed following the initialised schema '''
        if not self.validate(the_input):
            raise ValueError(self._validation_errors_payload_())

    def get_validated_input(self):
        ''' Validated input can be different if your schema included coercion '''
        return self.document

    def _validation_errors_payload_(self):
        errors = []
        for k, val in self.errors.items():
            errors.append({'field': k, 'message': val})

        return {
            'statusCode': 400,
            'status': 'ERR_VALIDATION',
            'errors': errors
        }


def format_apigw_response(status_code: int, status: str, payload: Dict[str, Any]):
    '''
    Simple utility to format a JSON response payload compatible with AWS API Gateway return format.
    Need to provide statusCode and status string to provide standardisation.
    '''
    payload["statusCode"] = status_code
    payload["status"] = status
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(payload)
    }


def get_secret():
    '''
    Utility method to retrieve the secrets from AWS Secrets Manager. Can optionally decrypt a
    base64 encoded secret value. Will return a KV dict
    '''
    secret = ""

    secret_name = os.environ['API_SECRET_NAME']
    region_name = os.environ['API_SECRET_REGION']

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
    except ClientError as err:
        raise err
    return secret
