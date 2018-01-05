"""
Health check convention.

Reports service health and basic information from the "/api/health" endpoint,
using HTTP 200/503 status codes to indicate healthiness.

"""
from distutils.util import strtobool
from microcosm.api import defaults

from microcosm_flask.audit import skip_logging
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.build_info import BuildInfo
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.errors import extract_error_message
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class HealthResult:
    def __init__(self, error=None, result=None):
        self.error = error
        self.result = result or "ok"

    def __nonzero__(self):
        return self.error is None

    def __bool__(self):
        return self.error is None

    def __str__(self):
        return self.result if self.error is None else self.error

    def to_dict(self):
        return {
            "ok": bool(self),
            "message": str(self),
        }

    @classmethod
    def evaluate(cls, func, graph):
        try:
            result = func(graph)
            return cls(result=result)
        except Exception as error:
            return cls(error=extract_error_message(error))


class Health:
    """
    Wrapper around service health state.

    May contain zero or more "checks" which are just callables that take the
    current object graph as input.

    The overall health is OK if all checks are OK.

    """
    def __init__(self, graph, include_build_info=True):
        self.graph = graph
        self.name = graph.metadata.name
        if include_build_info:
            self.checks = dict(
                build_num=BuildInfo.check_build_num,
                sha1=BuildInfo.check_sha1,
            )
        else:
            self.checks = dict()

    def to_dict(self):
        """
        Encode the name, the status of all checks, and the current overall status.

        """
        # evaluate checks
        checks = {
            key: HealthResult.evaluate(func, self.graph)
            for key, func in self.checks.items()
        }
        dct = dict(
            # return the service name helps for routing debugging
            name=self.name,
            ok=all(checks.values()),
        )
        if checks:
            dct["checks"] = {
                key: checks[key].to_dict()
                for key in sorted(checks.keys())
            }
        return dct


class HealthConvention(Convention):

    def __init__(self, graph, include_build_info=False):
        super(HealthConvention, self).__init__(graph)
        self.health = Health(graph, include_build_info)

    def configure_retrieve(self, ns, definition):

        @self.add_route(ns.singleton_path, Operation.Retrieve, ns)
        @skip_logging
        def current_health():
            response_data = self.health.to_dict()
            status_code = 200 if response_data["ok"] else 503
            return make_response(response_data, status_code=status_code)


@defaults(
    include_build_info="true",
)
def configure_health(graph):
    """
    Configure the health endpoint.

    :returns: a handle to the `Health` object, allowing other components to
              manipulate health state.
    """
    ns = Namespace(
        subject=Health,
    )

    include_build_info = strtobool(graph.config.health_convention.include_build_info)
    convention = HealthConvention(graph, include_build_info)
    convention.configure(ns, retrieve=tuple())
    return convention.health
