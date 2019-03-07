"""
Config sharing convention.

Reports service config protected by basic auth for securely running services
locally with realistic config.

"""
from json import dumps, loads

from microcosm.loaders.compose import PartitioningLoader

from microcosm_flask.audit import skip_logging
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class Config:
    """
    Wrapper around service config state.

    """
    def __init__(self, graph, include_build_info=True):
        self.graph = graph
        self.name = graph.metadata.name

    def to_dict(self):
        """
        Encode the name, the status of all checks, and the current overall status.

        """
        if not isinstance(self.graph.loader, PartitioningLoader):
            return dict(msg="Config sharing disabled for non-partioned loader")

        if not hasattr(self.graph.loader, "secrets"):
            return dict(msg="Config sharing disabled if no secrets are labelled")

        def remove_nulls(dct):
            return {key: value for key, value in dct.items() if value is not None}

        return loads(
            dumps(self.graph.loader.config, skipkeys=True, default=lambda obj: None),
            object_hook=remove_nulls,
        )


class ConfigDiscoveryConvention(Convention):

    def __init__(self, graph):
        super(ConfigDiscoveryConvention, self).__init__(graph)
        self.config_discovery = Config(graph)

    def configure_retrieve(self, ns, definition):
        @self.add_route(ns.singleton_path, Operation.Retrieve, ns)
        @skip_logging
        def current_config_discovery():
            response_data = self.config_discovery.to_dict()
            return make_response(response_data, status_code=200)


def configure_config(graph):
    """
    Configure the health endpoint.

    :returns: the current service configuration
    """
    ns = Namespace(
        subject=Config,
    )

    convention = ConfigDiscoveryConvention(
        graph,
    )
    convention.configure(ns, retrieve=tuple())
    return convention.config_discovery
