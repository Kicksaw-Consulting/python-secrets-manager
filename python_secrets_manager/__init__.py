from python_secrets_manager.utils import pull_aws_config_data, yml_to_dict


def get_secrets(environment: str, region_name: str = None):
    aws_secrets = yml_to_dict(environment)

    pulled_aws_secrets = pull_aws_config_data(aws_secrets, region_name=region_name)

    return pulled_aws_secrets


def inject_secrets(environment: str, settings_module, region_name: str = None):
    secrets = get_secrets(environment, region_name=region_name)

    for key, value in secrets.items():
        setattr(settings_module, key, value)
