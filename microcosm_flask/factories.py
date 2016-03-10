"""
Factories to configure Flask.

"""
from flask import Flask


def configure_flask(graph):
    """
    Create the Flask instance (only), bound to the "flask" key.

    Conventions should refer to `graph.flask` to avoid circular dependencies.

    """
    app = Flask(graph.metadata.name)
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
    Configure a Flask application with common convnetions, bound to the "app" key.

    """
    graph.use(
        "audit",
        "basic_auth",
        "error_handlers",
        "health",
        "logger",
        "route",
    )
    return graph.flask
