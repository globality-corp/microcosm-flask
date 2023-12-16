"""
Support for registering function metadata.

"""
import re
from collections.abc import Iterator

from werkzeug.exceptions import InternalServerError

from microcosm_flask.namespaces import Namespace


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


def parse_rule(rule: str) -> Iterator[tuple[str | None, str | None, str]]:
    """
    (this method disappeared from werkzeug after version 2.1.2. Just copied here
    for simplicity)

    Parse a rule and return it as generator. Each iteration yields tuples
    in the form ``(converter, arguments, variable)``. If the converter is
    `None` it's a static url part, otherwise it's a dynamic one.
    :internal:
    """
    pos = 0
    end = len(rule)
    _rule_re = re.compile(
        r"""
        (?P<static>[^<]*)                           # static rule data
        <
        (?:
            (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
            (?:\((?P<args>.*?)\))?                  # converter arguments
            \:                                      # variable delimiter
        )?
        (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
        >
        """,
        re.VERBOSE,
    )
    do_match = _rule_re.match
    used_names = set()
    while pos < end:
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        if data["static"]:
            yield None, None, data["static"]
        variable = data["variable"]
        converter = data["converter"] or "default"
        if variable in used_names:
            raise ValueError(f"variable name {variable!r} used twice.")
        used_names.add(variable)
        yield converter, data["args"] or None, variable
        pos = m.end()
    if pos < end:
        remaining = rule[pos:]
        if ">" in remaining or "<" in remaining:
            raise ValueError(f"malformed url rule: {rule!r}")
        yield None, None, remaining


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
