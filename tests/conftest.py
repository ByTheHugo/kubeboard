from dotenv import load_dotenv

load_dotenv(".flaskenv")

import logging
import pytest
from os import environ

logging.getLogger("kubernetes").setLevel(logging.INFO)

KUBERNETES_INGRESSES_NAMESPACE = "default"

FAVICON_HOSTNAME = "prometheus.io"
FAVICON_INVALID_HOSTNAME = "a.b.c.d"
FAVICON_URL = "https://prometheus.io/assets/favicons/android-chrome-192x192.png"

CONFIGURATION_ITEM_KEYS = ("name", "namespace", "annotations", "url", "icon")

ANNOTATIONS_TO_TEST = {
    f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/test": "success",
    "invalid-prefix/test": "fail",
}


@pytest.fixture(scope="session")
def logger() -> logging.Logger:
    return logging.getLogger(__name__)
