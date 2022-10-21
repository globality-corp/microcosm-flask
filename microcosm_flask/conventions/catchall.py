"""
Flask's default behavior is to return a 404 for a route the app can't match.
For backend services that are not queried directly by a front-end it can be useful
to specify a different HTTP code, to differentiate between a nonexistent resource
on a well-understood path (e.g. GET /user/123) and a nonexistent (e.g. GET /ursr).

In particular, this can allow a load-balancer to identify cases where it is routing a request
based on an outdated DNS entry, and to directly retry the request on a different instance.


"""
from microcosm.api import binding, defaults, typed
from werkzeug.exceptions import abort


@binding("catchall_convention")
@defaults(
    fallback_http_code=typed(int, default_value=501),
)
def configure_catchall_convention(graph):
    fallback_http_code = graph.config.catchall_convention.fallback_http_code

    @graph.flask.route("/<path:path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
    @graph.audit
    def catchall_route(path):
        abort(fallback_http_code, f"Unknown path {path}")

    return catchall_route
