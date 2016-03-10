"""
Health check convention.

Reports service health and basic information from the "/api/health" endpoint,
using HTTP 200/503 status codes to indicate healthiness.

"""
from flask import jsonify

from microcosm_flask.naming import singleton_path_for
from microcosm_flask.operations import Operation


class Health(object):
    """
    Wrapper around service health state.

    May contain zero or more "checks" which are just named booleans.
    The overall health is OK if all checks are OK.

    """
    def __init__(self, name):
        self.name = name
        self.checks = {}

    def to_dict(self):
        """
        Encode the name, the status of all checks, and the current overall status.

        Note that:

            >>> all([])
            True

        So the default overall status (in the absence of any checks) will be OK.

        """
        checks = {
            # If desired, synchronous checks can be implemented by providing
            # an object that implements __len__ or __nonzero__; both will be
            # evaluted upon boolean evaluation.
            key: bool(value)
            for key, value in self.checks.items()
        }
        return dict(
            # return the service name helps for routing debugging
            name=self.name,
            ok=all(checks.values()),
            checks=checks,
        )


def configure_health(graph):
    """
    Configure the health endpoint.

    :returns: a handle to the `Health` object, allowing other components to
              manipulate health state.
    """

    health = Health(name=graph.metadata.name)

    @graph.route(singleton_path_for(Health), Operation.Retrieve, Health)
    def current_health():
        dct = health.to_dict()
        response = jsonify(dct)
        response.status_code = 200 if dct["ok"] else 503
        return response

    return health
