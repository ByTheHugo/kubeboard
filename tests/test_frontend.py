from dotenv import load_dotenv

load_dotenv(".flaskenv")

from bs4 import BeautifulSoup
from app import create_app
from urllib.parse import quote_plus
from conftest import (
    CONFIGURATION_ITEM_KEYS,
    FAVICON_INVALID_HOSTNAME,
    FAVICON_HOSTNAME,
    FAVICON_URLS,
)
import cssutils


def TP_validate_index_endpoint(logger, config):
    logger.info(
        "Validating that the index HTML template is correctly generated using the index function..."
    )

    app = create_app()

    # Retrieve HTML by calling the function
    with app.test_client() as test_client:
        response = test_client.get("/")
        html_doc = response.text
        logger.debug(html_doc)
    assert html_doc, "Can't retrieve HTML!"

    # Parse it to validate the subtitle
    soup = BeautifulSoup(html_doc, "html.parser")  # Using the built-in Python parser
    subtitle = soup.h4
    assert len(subtitle) == 1, "No H4 tag found!"

    logger.debug(f"H4 tag found: {subtitle}")
    assert subtitle.get_text(strip=True) == config["theme"]["subtitle"]

    logger.info("HTML index is correctly generated.")


def TP_validate_config_endpoint(logger):
    logger.info(
        "Validating that the config output in JSON is correctly generated using the config function..."
    )

    app = create_app()

    # Retrieve the JSON configuration by calling the function
    with app.test_client() as test_client:
        response = test_client.get("/config")
        json = response.json
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


def TP_validate_theme_endpoint(logger, config):
    logger.info(
        "Validating that the theme CSS template is correctly generated using the theme function..."
    )

    app = create_app()

    # Retrieve the CSS theme by calling the function
    with app.test_client() as test_client:
        response = test_client.get("/static/css/kubeboard-theme.css")
        css = response.text
        logger.debug(css)
    assert css, "Can't retrieve CSS theme!"

    # Parse it to validate the theme rules
    sheet = cssutils.parseString(css)
    logger.debug(sheet.cssText)

    # Iterate over rule to validate
    for rule in sheet:
        logger.debug(f"Iterating over rule: {rule}")

        if rule.selectorText == "body":
            for property in rule.style:
                if property.name == "color":
                    assert property.value == config["theme"]["color"]["secondary"]
                if property.name == "backdrop-filter":
                    assert property.value == config["theme"]["background"]["effects"]

        if (
            rule.selectorText
            == ".app_item_details span, footer a, .active, header span, .bookmark_category h3"
        ):
            for property in rule.style:
                if property.name == "color":
                    assert property.value == config["theme"]["color"]["primary"]

        if rule.selectorText == "html":
            for property in rule.style:
                if property.name == "background":
                    assert (
                        property.value == f"url({config["theme"]["background"]["url"]})"
                    )

    logger.info("CSS theme is correctly generated.")


def TP_validate_javascript_endpoint(logger):
    logger.info(
        "Validating that the frontend JavaScript application is correctly generated using the frontend function..."
    )

    app = create_app()

    # Retrieve the CSS theme by calling the function
    with app.test_client() as test_client:
        response = test_client.get("/static/js/kubeboard.js")
        js = response.text
        logger.debug(js)
    assert js, "Can't retrieve JavaScript application!"


def TP_validate_favicon_endpoint(logger):
    logger.info(
        "Validating that the favicon endpoint is correctly returning favicon using the get_favicon function..."
    )

    app = create_app()

    # Retrieve the favicon by calling the function
    with app.test_client() as test_client:
        response = test_client.get(f"/favicon?hostname={quote_plus(FAVICON_HOSTNAME)}")
        favicon = response.json
        logger.debug(favicon)
    assert favicon, "Can't retrieve the favicon from endpoint!"

    # Validate the backend response
    assert "favicon" in favicon, f"Favicon response malformed: {favicon}!"
    assert (
        favicon["favicon"] in FAVICON_URLS
    ), f"Wrong favicon returned: {favicon["favicon"]}!"


def TP_validate_favicon_endpoint_without_param(logger):
    logger.info(
        "Validating that favicon endpoint without param is throwing BadRequest error..."
    )

    app = create_app()

    # Retrieve the favicon by calling the function
    with app.test_client() as test_client:
        response = test_client.get("/favicon")
        assert response.status_code == 400


def TP_validate_invalid_favicon_endpoint(logger):
    logger.info(
        "Validating that favicon endpoint with invalid favicon is throwing NotFound error..."
    )

    app = create_app()

    # Retrieve the favicon by calling the function
    with app.test_client() as test_client:
        response = test_client.get(
            f"/favicon?hostname={quote_plus(FAVICON_INVALID_HOSTNAME)}"
        )
        assert response.status_code == 404
