"""
Support for registering function metadata.

"""
from microcosm_flask.namespaces import Namespace
from werkzeug.exceptions import InternalServerError
from werkzeug.routing import parse_rule


REQUEST = "__request__"
RESPONSE = "__response__"
QS = "__qs__"


def iter_endpoints(graph, match_func):
    """
    Iterate through matching endpoints.

    The `match_func` is expected to have a signature of:

        def matches(operation, ns, rule):
            return True

    :returns: a generator over (`Operation`, `Namespace`, rule, func) tuples.

    """
    for rule in graph.flask.url_map.iter_rules():
        try:
            operation, ns = Namespace.parse_endpoint(rule.endpoint, get_converter(rule))
        except (IndexError, ValueError, InternalServerError):
            # operation follows a different convention (e.g. "static")
            continue
        else:
            # match_func gets access to rule to support path version filtering
            if match_func(operation, ns, rule):
                func = graph.flask.view_functions[rule.endpoint]
                yield operation, ns, rule, func


def get_converter(rule):
    """
    Parse rule will extract the converter from the rule as a generator

    We iterate through the parse_rule results to find the converter
    parse_url returns the static rule part in the first iteration
    parse_url returns the dynamic rule part in the second iteration if its dynamic

    """
    for converter, _, _ in parse_rule(str(rule)):
        if converter is not None:
            return converter
    return None


def request(schema):
    """
    Decorate a function with a request schema.

    """
    def wrapper(func):
        setattr(func, REQUEST, schema)
        return func
    return wrapper


def response(schema):
    """
    Decorate a function with a response schema.

    """
    def wrapper(func):
        setattr(func, RESPONSE, schema)
        return func
    return wrapper


def qs(schema):
    """
    Decorate a function with a query string schema.

    """
    def wrapper(func):
        setattr(func, QS, schema)
        return func
    return wrapper


def get_request_schema(func):
    return getattr(func, REQUEST, None)


def get_response_schema(func):
    return getattr(func, RESPONSE, None)


def get_qs_schema(func):
    return getattr(func, QS, None)
