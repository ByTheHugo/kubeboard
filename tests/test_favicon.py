from dotenv import load_dotenv

load_dotenv(".flaskenv")

from app.favicon import _favicon_fetch
from conftest import FAVICON_HOSTNAME, FAVICON_INVALID_HOSTNAME, FAVICON_URLS


# The favicon library used seems to be buggy when retrieving the favicon in SPA.
# That's why we run the test against a common static page.
def TP_validate_favicon_retrieval(logger):
    logger.info(
        "Validating that favicon can be retrieved using the _favicon_fetch function..."
    )

    favicon = _favicon_fetch(logger, FAVICON_HOSTNAME)
    logger.debug(f"Favicon(s) fetched: {favicon}")

    assert favicon, "No favicon was fetched!"
    assert (
        favicon in FAVICON_URLS
    ), f"Invalid favicon retrieved for {FAVICON_HOSTNAME}: {favicon}!"

    logger.info("Favicon was correctly fetched.")


def TP_validate_invalid_favicon_exception(logger):
    logger.info(
        "Validating that an invalid favicon can't be retrieved using the _favicon_fetch function..."
    )

    favicon = _favicon_fetch(logger, FAVICON_INVALID_HOSTNAME)
    logger.debug(f"Favicon(s) fetched: {favicon}")
    assert not favicon, "A favicon was fetched!"
