"""
A discovery endpoint provides links to other endpoints.

"""
from microcosm.api import defaults

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.linking import Link, Links
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPage, OffsetLimitPageSchema


def iter_links(operations, page):
    """
    Generate links for an iterable of operations on a starting page.

    """
    for operation, ns, rule, func in operations:
        yield Link.for_(
            operation=operation,
            ns=ns,
            type=ns.subject_name,
            qs=page.to_items(),
        )


class DiscoveryConvention(Convention):

    @property
    def matching_operations(self):
        return {
            Operation.from_name(operation_name)
            for operation_name in self.graph.config.discovery_convention.operations
        }

    def find_matching_endpoints(self, discovery_ns):
        """
        Compute current matching endpoints.

        Evaluated as a property to defer evaluation.

        """
        def match_func(operation, ns, rule):
            return operation in self.matching_operations

        return list(iter_endpoints(self.graph, match_func))

    def configure_discover(self, ns, definition):
        """
        Register a discovery endpoint for a set of operations.

        """
        page_schema = OffsetLimitPageSchema()

        @self.add_route("/", Operation.Discover, ns)
        def discover():
            # accept pagination limit from request
            page = OffsetLimitPage.from_query_string(page_schema)
            page.offset = 0

            response_data = dict(
                _links=Links({
                    "self": Link.for_(Operation.Discover, ns, qs=page.to_items()),
                    "search": [
                        link for link in iter_links(self.find_matching_endpoints(ns), page)
                    ],
                }).to_dict()
            )
            return make_response(response_data)


@defaults(
    name="hal",
    operations=[
        "search",
    ],
)
def configure_discovery(graph):
    """
    Build a singleton endpoint that provides a link to all search endpoints.

    """
    ns = Namespace(
        subject=graph.config.discovery_convention.name,
    )
    convention = DiscoveryConvention(graph)
    convention.configure(ns, discover=tuple())
    return ns.subject
