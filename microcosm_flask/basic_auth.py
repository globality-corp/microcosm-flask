"""
Basic Auth support.

Usage:

    @graph.app.route("/path")
    @graph.basic_auth.required
    def must_be_authorized():
        pass


"""
from base64 import b64encode

from flask_basicauth import BasicAuth
from microcosm.api import defaults
from werkzeug.exceptions import Unauthorized

from microcosm_flask.conventions.encoding import with_headers


def encode_basic_auth(username, password):
    """
    Encode basic auth credentials.

    """
    return "Basic {}".format(
        b64encode(
            "{}:{}".format(
                username,
                password,
            ).encode("utf-8")
        ).decode("utf-8")
    )


class ConfigBasicAuth(BasicAuth):
    """
    Basic auth decorator that pulls credentials from static configuration.

    This decorator is sufficient for internal service access control, but should
    not be used for anything truly sensitive.

    """

    def __init__(self, app, credentials):
        super(ConfigBasicAuth, self).__init__(app)
        self.credentials = credentials

    def check_credentials(self, username, password):
        """
        Override credential checking to use configured credentials.

        """
        return password is not None and self.credentials.get(username, None) == password

    def challenge(self):
        """
        Override challenge to raise an exception that will trigger regular error handling.

        """
        response = super(ConfigBasicAuth, self).challenge()
        raise with_headers(Unauthorized(), response.headers)


@defaults(
    credentials=dict(
        # set a default configuration but don't merge it if other config is set
        __merge__=False,
        default="secret",
    ),
)
def configure_basic_auth_decorator(graph):
    """
    Configure a basic auth decorator.

    """
    # use the metadata name if no realm is defined
    graph.config.setdefault("BASIC_AUTH_REALM", graph.metadata.name)
    return ConfigBasicAuth(
        app=graph.flask,
        # wrap in dict to allow lists of items as well as dictionaries
        credentials=dict(graph.config.basic_auth.credentials),
    )
