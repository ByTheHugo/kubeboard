from app.kubernetes import k8s_load_config, k8s_get_ingresses
from app.favicon import _favicon_fetch
from cachetools import TTLCache
from flask import Flask, render_template, request, abort
from markupsafe import escape
from os import getenv

# Create the Flask application
app = Flask(__name__)
app.config.from_prefixed_env()

# Cache favicon in RAM (for now)
favicon_cache = TTLCache(
    maxsize=int(getenv("FLASK_FAVICON_CACHE_SIZE")),
    ttl=int(getenv("FLASK_FAVICON_CACHE_TTL")),
)


# Application routes below
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html.j2", subtitle=escape(app.config["APP_SUBTITLE"]))


@app.route("/config", methods=["GET"])
def config():
    # Start by loading the Kubernetes configuration
    k8s_load_config(logger=app.logger)

    # Fetch all the ingresses from Kubernetes API
    ingresses = k8s_get_ingresses(
        logger=app.logger,
        prefix=app.config["K8S_ANNOTATION_PREFIX"],
        default_icon=escape(app.config["APP_DEFAULT_ICON"]),
        hide_by_default=app.config["APP_HIDE_BY_DEFAULT"],
    )

    # Hydrate ingresses with favicon (if in cache)
    for ingress in ingresses:
        if ingress["url"] in favicon_cache:
            ingress["favicon"] = favicon_cache[ingress["url"]]

    # Return to user
    return ingresses


@app.route("/static/css/kubeboard-theme.css", methods=["GET"])
def theme():
    resp = app.make_response(
        render_template(
            "theme.css.j2",
            primary_color=escape(app.config["THEME_PRIMARY_COLOR"]),
            secondary_color=escape(app.config["THEME_SECONDARY_COLOR"]),
            background_url=escape(app.config["THEME_BACKGROUND_URL"]),
            background_effects=escape(app.config["THEME_BACKGROUND_EFFECTS"]),
        )
    )
    resp.mimetype = "text/css"
    return resp


@app.route("/static/js/kubeboard.js", methods=["GET"])
def frontend():
    # Convert Python boolean to JS boolean
    fetch_favicon = "true" if app.config["APP_FETCH_FAVICON"] else "false"
    resp = app.make_response(
        render_template("app.js.j2", fetch_favicon=escape(fetch_favicon))
    )
    resp.mimetype = "text/javascript"
    return resp


@app.route("/favicon", methods=["GET"])
def get_favicon():
    # Validate request parameters
    hostname = request.args.get("hostname")
    if not hostname:
        abort(400)

    # Check if favicon is present in cache
    # and retrieve it if not
    if hostname not in favicon_cache:
        favicon_cache[hostname] = _favicon_fetch(app.logger, hostname)

    # Return JSON to user if a favicon was found
    if hostname not in favicon_cache or not favicon_cache[hostname]:
        abort(404)
    return {"favicon": favicon_cache[hostname]}
