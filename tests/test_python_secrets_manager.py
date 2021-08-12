import boto3
import json

from moto import mock_secretsmanager

from python_secrets_manager import get_secrets
from python_secrets_manager.utils import yml_to_dict


def test_yml_to_dict():
    secrets = yml_to_dict("test")

    assert secrets == {"secret-name": ["KEY1", "KEY2"]}


@mock_secretsmanager
def test_get_secrets():
    client = boto3.client("secretsmanager", region_name="us-west-2")
    client.create_secret(
        Name="secret-name",
        SecretString=json.dumps({"KEY1": "hello", "KEY2": "world"}),
    )
    secrets = get_secrets("test", region_name="us-west-2")
    assert secrets == {"KEY1": "hello", "KEY2": "world"}
