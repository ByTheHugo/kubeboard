from dotenv import load_dotenv

load_dotenv(".flaskenv")

from os import path, environ
from yaml import safe_load, YAMLError
import logging
import pytest

logging.getLogger("kubernetes").setLevel(logging.INFO)

KUBERNETES_INGRESSES_NAMESPACE = "default"

FAVICON_HOSTNAME = "prometheus.io"
FAVICON_INVALID_HOSTNAME = "a.b.c.d"
FAVICON_URLS = [
    "https://prometheus.io/assets/favicons/android-chrome-192x192.png",
    "https://prometheus.io/opengraph-image.png?b370f6418ef38b42",
    "https://prometheus.io/icon.svg?7aa022e51797bcef",
]

CONFIGURATION_ITEM_KEYS = ("name", "namespace", "annotations", "url", "icon")

ANNOTATIONS_TO_TEST = {
    f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/test": "success",
    "invalid-prefix/test": "fail",
}


@pytest.fixture(scope="session")
def logger() -> logging.Logger:
    return logging.getLogger(__name__)


@pytest.fixture(scope="session")
def config() -> dict:
    # Determine the path to your config.yml file
    # This assumes config.yml is in the same directory as your app.py
    config_path = path.join(path.dirname(__file__), "../kubeboard.yaml")

    # Load configuration from the YAML file
    with open(config_path, "r") as f:
        yaml_config = safe_load(f)
    return yaml_config
