from dotenv import load_dotenv

load_dotenv(".flaskenv")

from bs4 import BeautifulSoup
from app import app, index, theme, config, get_favicon, frontend
from os import environ
from urllib.parse import quote_plus
from werkzeug.exceptions import BadRequest, NotFound
from conftest import (
    CONFIGURATION_ITEM_KEYS,
    FAVICON_INVALID_HOSTNAME,
    FAVICON_HOSTNAME,
    FAVICON_URL,
)
import cssutils


def TP_validate_index_endpoint(logger):
    logger.info(
        "Validating that the index HTML template is correctly generated using the index function..."
    )

    # Retrieve HTML by calling the function
    with app.app_context(), app.test_request_context():
        html_doc = index()
        logger.debug(html_doc)
    assert html_doc, "Can't retrieve HTML!"

    # Parse it to validate the subtitle
    soup = BeautifulSoup(html_doc, "html.parser")  # Using the built-in Python parser
    subtitle = soup.h4
    assert len(subtitle) > 0, "No H4 tag found!"

    logger.debug(f"H4 tag found: {subtitle}")
    assert subtitle.get_text(strip=True) == environ["FLASK_APP_SUBTITLE"]

    logger.info("HTML index is correctly generated.")


def TP_validate_config_endpoint(logger):
    logger.info(
        "Validating that the config output in JSON is correctly generated using the config function..."
    )

    # Retrieve the JSON configuration by calling the function
    with app.app_context(), app.test_request_context():
        json = config()
        logger.debug(json)
    assert json, "Can't retrieve configuration JSON!"

    # Validate configuration data
    assert len(json) > 0, "No configuration item returned by the /config endpoint!"
    for item in json:
        logger.debug(f"Iterating over {item}")
        assert all(
            k in item for k in CONFIGURATION_ITEM_KEYS
        ), f"Configuration item is misformed: {item}"

    logger.info("JSON configuration is correctly generated.")


def TP_validate_theme_endpoint(logger):
    logger.info(
        "Validating that the theme CSS template is correctly generated using the theme function..."
    )

    # Retrieve the CSS theme by calling the function
    with app.app_context(), app.test_request_context():
        css = theme()
        logger.debug(css)
    assert css, "Can't retrieve CSS theme!"

    # Parse it to validate the theme rules
    sheet = cssutils.parseString(css.get_data(True))
    logger.debug(sheet.cssText)

    # Iterate over rule to validate
    for rule in sheet:
        logger.debug(f"Iterating over rule: {rule}")

        if rule.selectorText == "body":
            for property in rule.style:
                if property.name == "color":
                    assert property.value == environ["FLASK_THEME_SECONDARY_COLOR"]
                if property.name == "backdrop-filter":
                    assert property.value == environ["FLASK_THEME_BACKGROUND_EFFECTS"]

        if (
            rule.selectorText
            == ".app_item_details span, .active, header span, footer a"
        ):
            for property in rule.style:
                if property.name == "color":
                    assert property.value == environ["FLASK_THEME_PRIMARY_COLOR"]

        if rule.selectorText == "html":
            for property in rule.style:
                if property.name == "background":
                    assert (
                        property.value
                        == f"url({environ["FLASK_THEME_BACKGROUND_URL"]})"
                    )

    logger.info("CSS theme is correctly generated.")


def TP_validate_javascript_endpoint(logger):
    logger.info(
        "Validating that the frontend JavaScript application is correctly generated using the frontend function..."
    )

    # Retrieve the CSS theme by calling the function
    with app.app_context(), app.test_request_context():
        js = frontend()
        logger.debug(js)
    assert js, "Can't retrieve JavaScript application!"


def TP_validate_favicon_endpoint(logger):
    logger.info(
        "Validating that the favicon endpoint is correctly returning favicon using the get_favicon function..."
    )

    # Retrieve the favicon by calling the function
    with app.app_context(), app.test_request_context(
        path=f"/favicon?hostname={quote_plus(FAVICON_HOSTNAME)}"
    ):
        favicon = get_favicon()
        logger.debug(favicon)
    assert favicon, "Can't retrieve the favicon from endpoint!"

    # Validate the backend response
    assert "favicon" in favicon, f"Favicon response malformed: {favicon}!"
    assert (
        favicon["favicon"] == FAVICON_URL
    ), f"Wrong favicon returned: {favicon["favicon"]}!"


def TP_validate_favicon_endpoint_without_param():
    # Retrieve the favicon by calling the function
    with app.app_context(), app.test_request_context():
        try:
            get_favicon()
        except BadRequest:
            assert True


def TP_validate_invalid_favicon_endpoint():
    # Retrieve the favicon by calling the function
    with app.app_context(), app.test_request_context(
        path=f"/favicon?hostname={quote_plus(FAVICON_INVALID_HOSTNAME)}"
    ):
        try:
            get_favicon()
        except NotFound:
            assert True
