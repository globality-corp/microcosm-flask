"""
Path building.

"""
from microcosm.api import defaults


@defaults(
    prefix="/api",
)
class RoutePathBuilder:

    def __init__(self, graph):
        self.prefix = graph.config.build_route_path.prefix

    def __call__(self, path, prefix=None):
        """
        Generate a path for a route.

        :param path: the route path; must not be None
        :param prefix: overrides the default prefix if not None

        """
        return "/" + "/".join(filter(None, self.iter_path_parts(path, prefix)))

    def iter_path_parts(self, path, prefix):
        # use the provided prefix is not None
        if prefix is not None:
            yield prefix.strip("/")
        else:
            yield self.prefix.strip("/")

        # use the path
        yield path.strip("/")
