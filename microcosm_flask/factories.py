"""
Factories to configure Flask.

"""
import microcosm.opaque  # noqa
from flask import Flask
from microcosm.api import defaults


@defaults(
    port=5000,
    enable_profiling=False,
    profile_dir=None,
)
def configure_flask(graph):
    """
    Create the Flask instance (only), bound to the "flask" key.

    Conventions should refer to `graph.flask` to avoid circular dependencies.

    """
    app = Flask(graph.metadata.import_name)
    app.debug = graph.metadata.debug
    app.testing = graph.metadata.testing

    # copy in the graph's configuration for non-nested keys
    app.config.update({
        key: value
        for key, value in graph.config.items()
        if not isinstance(value, dict)
    })

    return app


def configure_flask_app(graph):
    """
    Configure a Flask application with common conventions, bound to the "app" key.

    """
    graph.use(
        "audit",
        "request_context",
        "basic_auth",
        "error_handlers",
        "logger",
        "opaque",
    )
    return graph.flask
