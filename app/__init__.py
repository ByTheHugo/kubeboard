from app.kubernetes import k8s_load_config, k8s_get_ingresses
from app.configuration import _configuration_load
from app.favicon import _favicon_fetch
from cachetools import TTLCache
from flask import Flask, render_template, request, abort
from markupsafe import escape
from os import path, environ, getcwd


# Create the Flask application
def create_app(configuration_filepath=environ["FLASK_CONFIGURATION_FILE"]):
    app = Flask(__name__)
    app.config.from_prefixed_env()

    # Load configuration from the YAML file
    yaml_config = _configuration_load(
        app.logger,
        path.join(getcwd(), configuration_filepath),
        path.join(app.root_path, "..", app.config["CONFIGURATION_SCHEMA"]),
    )
    app.config.update(yaml_config)

    # Cache favicon in RAM (for now)
    favicon_cache = TTLCache(
        maxsize=int(app.config["FAVICON_CACHE_SIZE"]),
        ttl=int(app.config["FAVICON_CACHE_TTL"]),
    )

    # Application routes below
    @app.route("/", methods=["GET"])
    def index():
        return render_template(
            "index.html.j2",
            subtitle=escape(app.config["theme"]["subtitle"]),
            bookmarks=app.config["bookmarks"] if "bookmarks" in app.config else {},
            default_icon=escape(app.config["theme"]["defaultIcons"]["bookmark"]),
            logo=app.config["theme"]["logo"],
        )

    @app.route("/config", methods=["GET"])
    def config():
        # Start by loading the Kubernetes configuration
        k8s_load_config(logger=app.logger)

        # Fetch all the ingresses from Kubernetes API
        ingresses = k8s_get_ingresses(
            logger=app.logger,
            prefix=app.config["K8S_ANNOTATION_PREFIX"],
            default_icon=escape(app.config["theme"]["defaultIcons"]["ingress"]),
            hide_by_default=app.config["hideByDefault"],
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
                primary_color=escape(app.config["theme"]["color"]["primary"]),
                secondary_color=escape(app.config["theme"]["color"]["secondary"]),
                background_url=escape(app.config["theme"]["background"]["url"]),
                background_effects=escape(app.config["theme"]["background"]["effects"]),
            )
        )
        resp.mimetype = "text/css"
        return resp

    @app.route("/static/js/kubeboard.js", methods=["GET"])
    def frontend():
        # Convert Python boolean to JS boolean
        fetch_favicon = "true" if app.config["fetchFavicon"] else "false"
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

    return app
