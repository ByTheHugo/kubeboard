from logging import Logger
from yaml import safe_load
from sys import exit
from jsonschema import validate
from json import load


def _configuration_load_schema(logger: Logger, filepath: str) -> dict:
    try:
        with open(filepath, "r") as f:
            schema_json = load(f)
            return schema_json
    except FileNotFoundError:
        logger.error(f"Schema definition not found at {filepath}. Exiting...")
        exit(-1)


def _configuration_load(logger: Logger, filepath: str, schema_filepath: str) -> dict:
    # Load configuration from the YAML file
    try:
        with open(filepath, "r") as f:
            yaml_config = safe_load(f)
            schema_json = _configuration_load_schema(logger, schema_filepath)

            validate(yaml_config, schema=schema_json)

            return yaml_config

    except FileNotFoundError:
        logger.error(f"Configuration file not found at {filepath}. Exiting...")
        exit(-1)
