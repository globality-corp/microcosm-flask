"""
Serve build information.

"""
from microcosm.api import defaults
from microcosm_flask.audit import skip_logging
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class BuildInfo(object):

    def __init__(self, build_num, sha1):
        self.build_num = build_num
        self.sha1 = sha1

    def to_dict(self):
        return dict(
            build_num=self.build_num,
            sha1=self.sha1,
        )


class BuildInfoConvention(Convention):

    def __init__(self, graph):
        super(BuildInfoConvention, self).__init__(graph)
        self.build_info = BuildInfo(
            build_num=graph.config.build_info_convention.build_num,
            sha1=graph.config.build_info_convention.sha1,
        )

    def configure_retrieve(self, ns, definition):

        @self.add_route(ns.singleton_path, Operation.Retrieve, ns)
        @skip_logging
        def build_info():
            response_data = self.build_info.to_dict()
            return make_response(response_data)


@defaults(
    path_prefix="",
    build_num=None,
    sha1=None,
)
def configure_build_info(graph):
    """
    Configure the build info endpoint.

    """
    ns = Namespace(
        path=graph.config.build_info_convention.path_prefix,
        subject=BuildInfo,
    )

    convention = BuildInfoConvention(graph)
    convention.configure(ns, retrieve=tuple())
    return convention.build_info
