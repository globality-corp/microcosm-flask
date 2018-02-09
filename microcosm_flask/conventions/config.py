"""
Config sharing convention.

Reports service config protected by basic auth for securely running services
locally with realistic config.

"""
from distutils.util import strtobool
from json import dumps, loads

from microcosm.api import defaults
from microcosm.object_graph import config_report
from microcosm_flask.audit import skip_logging
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.build_info import BuildInfo
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.errors import extract_error_message
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class Config:
    """
    Wrapper around service config state.

    """
    def __init__(self, graph, include_build_info=True):
        self.graph = graph
        self.name = graph.metadata.name
        self.config = dict(
            self.graph.config
        )

    def to_dict(self):
        """
        Encode the name, the status of all checks, and the current overall status.

        """
        def remove_nulls(dct):
            return {key: value for key, value in dct.items() if value is not None}

        # evaluate checks
        return loads(
            dumps(self.config, skipkeys=True, default=lambda obj: None),
            object_hook=remove_nulls,
        )


class ConfigDiscoveryConvention(Convention):

    def __init__(self, graph, enabled):
        super(ConfigDiscoveryConvention, self).__init__(graph)
        self.config_discovery = Config(graph)
        self.enabled = enabled

    def configure_retrieve(self, ns, definition):
        if not self.enabled:
            return

        @self.add_route(ns.singleton_path, Operation.Retrieve, ns)
        @self.graph.basic_auth.required
        @skip_logging
        def current_config_discovery():
            response_data = self.config_discovery.to_dict()
            return make_response(response_data, status_code=200)


@defaults(
    enabled="False",
)
def configure_config(graph):
    """
    Configure the health endpoint.

    :returns: the current service configuration
    """
    ns = Namespace(
        subject=Config,
    )
    print(ns.singleton_path)

    convention = ConfigDiscoveryConvention(
        graph,
        enabled=strtobool(graph.config.config_convention.enabled),
    )
    convention.configure(ns, retrieve=tuple())
    return convention.config_discovery
