"""
Flask's default behavior is to return a 404 for a route the app can't match.
For backend services that are not queried directly by a front-end it can be useful
to specify a different HTTP code, to differentiate between a nonexistent resource
on a well-understood path (e.g. GET /user/123) and a nonexistent (e.g. GET /ursr).

In particular, this can allow a reverse-proxy to identify cases where it is routing a request
based on an outdated DNS entry.


"""
from microcosm.api import binding, defaults, typed


@binding("catchall_convention")
@defaults(
    fallback_http_code=typed(int, default_value=421),
)
def configure_catchall_convention(graph):
    fallback_http_code = graph.config.catchall_convention.fallback_http_code

    @graph.flask.route("/<path:path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
    def catch_all(path):
        return "Unknown path", fallback_http_code

    return catch_all
