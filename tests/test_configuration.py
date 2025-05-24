from dotenv import load_dotenv

load_dotenv(".flaskenv")

import pytest
from app import create_app
from os import environ, path
from jsonschema import ValidationError
from app.configuration import _configuration_load_schema, _configuration_load
from os import path, environ


def TP_validate_schema_loading(logger):
    logger.info(
        "Validating the configuration JSON schema is correctly loaded using the _configuration_load_schema function..."
    )
    _configuration_load_schema(
        logger,
        path.join(
            path.dirname(path.realpath(__file__)),
            "..",
            environ["FLASK_CONFIGURATION_SCHEMA"],
        ),
    )


@pytest.mark.xfail
def TP_validate_unexisting_schema_loading(logger):
    logger.info(
        "Validating that a non-existing configuration JSON schema is throwing error when using the _configuration_load_schema function..."
    )
    _configuration_load_schema(
        logger,
        path.join("nonexistingconfig"),
    )


@pytest.mark.xfail
def TP_validate_unexisting_configurationloading(logger):
    logger.info(
        "Validating that a non-existing configuration is throwing error when using the _configuration_load function..."
    )
    _configuration_load(
        logger,
        path.join("nonexistingconfig"),
        path.join(
            path.dirname(path.realpath(__file__)),
            "..",
            environ["FLASK_CONFIGURATION_SCHEMA"],
        ),
    )


def TP_validate_configuration(logger):
    logger.info(
        "Validating that configuration is successfully parsed then loaded into Flask..."
    )

    config_keys = ["hideByDefault", "fetchFavicon", "theme", "bookmarks"]
    app = create_app()

    with app.app_context():
        logger.debug(app.config)

        for key in config_keys:
            assert (
                key in app.config
            ), f"Configuration key {key} not found in kubeboard.yaml!"


def TP_validate_misformed_configuration(logger):
    logger.info(
        "Validating that misformed configuration is throwing error then loaded into Flask..."
    )

    try:
        create_app(
            path.join(
                path.dirname(path.realpath(__file__)), "files/kubeboard.invalid.yaml"
            )
        )
        assert False  # pragma: no cover
    except ValidationError:
        assert True
