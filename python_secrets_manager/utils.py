import boto3
import base64
import json
import yaml

from logging import getLogger
from pathlib import Path

from python_secrets_manager.root import SM_CONFIG_ROOT

logger = getLogger(__name__)


def _validate_yml(secrets: dict):
    seen = list()

    for secret_name in secrets:
        for param in secrets[secret_name]:
            if param not in seen:
                seen.append(param)
            else:
                raise AssertionError(f"{param} in multiple secrets!")


def yml_to_dict(environment: str):
    secrets_file = ""

    yaml_file = Path(SM_CONFIG_ROOT) / f"secrets-manager-{environment}.yaml"
    yml_file = Path(SM_CONFIG_ROOT) / f"secrets-manager-{environment}.yml"

    if yaml_file.exists():
        secrets_file = yaml_file
    elif yml_file.exists():
        secrets_file = yml_file

    if not secrets_file:
        logger.warning(f"No file found for secrets-manager-{environment}.yml|yaml")

    try:
        with open(secrets_file, "r") as yml:
            secrets: dict = yaml.safe_load(yml)
    except FileNotFoundError:
        secrets = {}

    _validate_yml(secrets)

    return secrets


def get_secret(secret_name, region_name=None):
    client = boto3.client("secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        secret = get_secret_value_response["SecretString"]
    else:
        secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secret


def parse_secret(secret_name: str, secret_keys: list, region_name=None) -> dict:
    secret_object = json.loads(get_secret(secret_name, region_name=region_name))
    secrets = dict()
    for secret_key in secret_keys:
        assert (
            secret_key in secret_object
        ), f"{secret_name} doesn't contain the key {secret_key}"
        secrets[secret_key] = secret_object[secret_key]
    return secrets


def pull_aws_config_data(data: dict, region_name=None):
    pulled = dict()
    for key, secret_keys in data.items():
        secret_object = parse_secret(key, secret_keys, region_name=region_name)
        pulled = {**pulled, **secret_object}
    return pulled
