"""
Expose/manage logging levels.

"""
from collections import namedtuple
from logging import PlaceHolder, root

from marshmallow import fields, Schema
from microcosm.api import defaults

from microcosm_flask.conventions.base import Convention, EndpointDefinition
from microcosm_flask.conventions.encoding import dump_response_data
from microcosm_flask.conventions.registry import response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


Logger = namedtuple("Logger", ["name", "level", "logger", "children"])


def dehumanize_level(value):
    return {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 30,
        "CRITICAL": 50,
    }[value]


def humanize_level(value):
    try:
        return {
            0: "NOTSET",
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
            50: "CRITICAL",
        }[int(value)]
    except Exception:
        return value


def make_logger_node(name, logger, parent=None):
    if isinstance(logger, PlaceHolder):
        # some loggers are instances of logging.PlaceHolder
        level = parent.level
    else:
        level = humanize_level(logger.getEffectiveLevel())

    node = Logger(name, level, logger, [])
    if parent is not None:
        parent.children.append(node)
    return node


def build_logger_tree():
    """
    Build a DFS tree representing the logger layout.

    Adapted with much appreciation from: https://github.com/brandon-rhodes/logging_tree

    """
    cache = {}
    tree = make_logger_node("", root)
    for name, logger in sorted(root.manager.loggerDict.items()):
        if "." in name:
            parent_name = ".".join(name.split(".")[:-1])
            parent = cache[parent_name]
        else:
            parent = tree

        cache[name] = make_logger_node(name, logger, parent)
    return tree


class LoggerSchema(Schema):
    name = fields.String(required=True)
    level = fields.String(required=True)
    children = fields.List(fields.Nested("LoggerSchema"), required=True)


class LoggingLevelConvention(Convention):
    """
    Convention that exposing logging configuration.

    Includes a `GET` request to retrieve the current logging tree and a `PATCH` request
    to (temporarily) change logging levels.

    """
    def __init__(self, graph):
        super(LoggingLevelConvention, self).__init__(graph)
        self.max_duration = float(graph.config.logging_level_convention.max_duration)

    def configure_retrieve(self, ns, definition):
        response_schema = definition.response_schema

        @self.add_route(ns.singleton_path, Operation.Retrieve, ns)
        @response(response_schema)
        def retrieve():
            logger_tree = build_logger_tree()
            return dump_response_data(response_schema, logger_tree)


@defaults(
    max_duration=300.0,
)
def configure_logging_level(graph):
    ns = Namespace(
        subject="logging_level",
    )

    convention = LoggingLevelConvention(graph)
    convention.configure(
        ns,
        retrieve=EndpointDefinition(
            response_schema=LoggerSchema(),
        ),
    )
    return ns
