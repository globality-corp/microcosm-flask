"""
Factories to configure Flask.

"""
from decimal import Decimal
from typing import Any

import microcosm.opaque  # noqa
import simplejson
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from microcosm.api import defaults


class FlaskV1JSONProvider(DefaultJSONProvider):
    """
    A JSON provider that brings back flask v1 behavior.
    That is decimals are not converted to strings but serialised as
    a float with all the precision included.
    """

    def __init__(self, app):
        super().__init__(app)

    @staticmethod
    def default(o: Any) -> Any:
        if isinstance(o, Decimal):
            return o
        return DefaultJSONProvider.default(o)

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        """Serialize data as JSON to a string.
        Keyword arguments are passed to :func:`json.dumps`. Sets some
        parameter defaults from the :attr:`default`,
        :attr:`ensure_ascii`, and :attr:`sort_keys` attributes.
        :param obj: The data to serialize.
        :param kwargs: Passed to :func:`json.dumps`.
        """
        kwargs.setdefault("default", self.default)
        kwargs.setdefault("ensure_ascii", self.ensure_ascii)
        kwargs.setdefault("sort_keys", self.sort_keys)
        return simplejson.dumps(obj, **kwargs)

    def loads(self, s: str | bytes, **kwargs: Any) -> Any:
        """Deserialize data as JSON from a string or bytes.
        :param s: Text or UTF-8 bytes.
        :param kwargs: Passed to :func:`json.loads`.
        """
        return simplejson.loads(s, **kwargs)


def patch_flask_jsonifier(graph):
    graph.flask.json = FlaskV1JSONProvider(graph.flask)


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
    patch_flask_jsonifier(graph)
    return graph.flask
