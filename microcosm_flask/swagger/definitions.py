"""
Generates a Swagger definition for registered endpoints.

Note that:
 -  Swagger operations and type names use different conventions from the internal definitions
    because we want to make usage friendly for code generation (e.g. bravado)

 -  Marshmallow to JSON Schema conversion is somewhat simplistic. There are several projects
    that already implement this conversion that we could try adapting. At the moment, the
    overhead of adapting another library's conventions is too high.

 -  All resource definitions are assumed to be shared and are declared in the "definitions"
    section of the result.

 -  All errors are defined generically.


"""
from enum import Enum, unique
from logging import getLogger
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from urllib.parse import unquote

from flask.globals import _request_ctx_stack
from openapi import model as swagger
from werkzeug.routing import BuildError, Rule

from microcosm_flask.conventions.registry import (
    get_qs_schema,
    get_request_schema,
    get_response_schema,
)
from microcosm_flask.errors import ErrorContextSchema, ErrorSchema, SubErrorSchema
from microcosm_flask.namespaces import Namespace
from microcosm_flask.naming import name_for
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.api import build_parameter, iter_schemas
from microcosm_flask.swagger.naming import operation_name, type_name


logger = getLogger("microcosm_flask.swagger")
# Placeholder integer id used to build URIs in werkzeug before replacing with id param name.
# Use a value that is unlikely to be present somewhere else in the URI.
PLACEHOLDER_INTEGER_ID = 1111


@unique
class RequestSide(Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    BOTH = "BOTH"


def build_swagger(graph, ns, operations, validate_schema=False):
    """
    Build out the top-level swagger definition.

    """
    base_path = graph.build_route_path(ns.path, ns.prefix)
    schema = swagger.Swagger(
        swagger="2.0",
        info=swagger.Info(
            title=graph.metadata.name,
            version=ns.version,
        ),
        consumes=swagger.MediaTypeList([
            swagger.MimeType("application/json"),
        ]),
        produces=swagger.MediaTypeList([
            swagger.MimeType("application/json"),
        ]),
        basePath=base_path,
        paths=swagger.Paths(),
        definitions=swagger.Definitions(),
    )
    add_paths(schema.paths, base_path, operations)
    add_definitions(schema.definitions, operations)

    if validate_schema:
        try:
            schema.validate()
        except Exception:
            logger.exception("Swagger definition did not validate against swagger schema")
            raise

    return schema


def _construct_schema_request_arguments():
    """
    Create a mapping between a given endpoint/method and its possible arguments.
    Used in aid of generating paths during swagger generation

    """
    reqctx = _request_ctx_stack.top
    url_adapter = reqctx.url_adapter
    rules: List[Rule] = url_adapter.map._rules

    return {
        (rule.endpoint, method): rule.arguments
        for rule in rules
        for method in rule.methods
    }


def add_paths(paths, base_path, operations):
    """
    Add paths to swagger.

    """
    schema_request_arguments = _construct_schema_request_arguments()

    for operation, ns, rule, func in operations:
        path = build_path(operation, ns, schema_request_arguments)
        if not path.startswith(base_path):
            continue
        method = operation.value.method.lower()
        # If there is no version number or prefix, we'd expect the base path to be ""
        # However, OpenAPI requires the minimal base path to be "/"
        # This means we need branching logic for that special case
        suffix_start = 0 if len(base_path) == 1 else len(base_path)
        paths.setdefault(
            path[suffix_start:],
            swagger.PathItem(),
        )[method] = build_operation(operation, ns, rule, func)


def add_definitions(definitions, operations):
    """
    Add definitions to swagger.

    """
    for definition_schema, request_side in iter_definitions(definitions, operations):
        if definition_schema is None:
            continue
        if isinstance(definition_schema, str):
            continue

        for name, schema in iter_schemas(definition_schema, strict_enums=request_side != RequestSide.RESPONSE):
            definitions.setdefault(name, swagger.Schema(schema))


def iter_definitions(definitions, operations):
    """
    Generate definitions to be converted to swagger schema.

    """
    # general error schema per errors.py
    for error_schema_class in [ErrorSchema, ErrorContextSchema, SubErrorSchema]:
        yield error_schema_class(), RequestSide.BOTH

    # add all request and response schemas
    for operation, obj, rule, func in operations:
        yield get_request_schema(func), RequestSide.REQUEST
        yield get_response_schema(func), RequestSide.RESPONSE


def build_path_for_integer_param(ns, operation, arguments: Set):
    """
    Build an endpoint path when the parameters are integer-valued

    When building paths for swagger, parameter names are substituted for
    path parameters. For example, the output will have '/api/v1/person/{person_id}'.
    We still use werkzeug to build those paths with placeholders for params.

    That works with UUID-valued ids but not integer-valued ones, due do a difference
    between the UUIDConverter and NumberConverter's `to_url` methods
    (see https://github.com/pallets/werkzeug/blob/master/src/werkzeug/routing.py#L1315
    and https://github.com/pallets/werkzeug/blob/master/src/werkzeug/routing.py#L1234)

    Here we instead use placeholder integers to use werkzeug functions, and replace
    them afterwards.

    """
    ordered_args = list(arguments)
    args_substitution = {
        PLACEHOLDER_INTEGER_ID + index: argument
        for index, argument in enumerate(ordered_args)
    }
    uri_templates = {
        argument: f"{placeholder}"
        for placeholder, argument in args_substitution.items()
    }
    path = unquote(ns.url_for(operation, _external=False, **uri_templates))
    for placeholder_integer, argument in args_substitution.items():
        path = path.replace(str(placeholder_integer), f"{{{argument}}}")

    return path


def create_uri_templates(arguments):
    return {
        argument: f"{{{argument}}}"
        for argument in arguments
    }


def build_path(operation: Operation, ns: Namespace, schema_request_arguments: Optional[Dict[Tuple, List[str]]] = None):
    expected_arguments: List[str] = (
        schema_request_arguments.get((ns.endpoint_for(operation), operation.value.method), [])
        if schema_request_arguments
        else []
    )

    expected_uri_templates = create_uri_templates(expected_arguments)

    try:
        # flask will sometimes try to quote '{' and '}' characters
        return unquote(ns.url_for(operation, _external=False, **expected_uri_templates))
    except (BuildError, ValueError) as error:
        # NB: The arguments were misidentified in the previous step, use the ones supplied by the error
        actual_arguments = (
            error.suggested.arguments   # type: ignore
            if isinstance(error, BuildError)
            else expected_arguments
        )

        if ns.identifier_type == "int":
            return build_path_for_integer_param(ns, operation, actual_arguments)  # type: ignore
        else:
            # we are missing some URI path parameters
            uri_templates = create_uri_templates(actual_arguments)
            return unquote(ns.url_for(operation, _external=False, **uri_templates))


def body_param(schema):
    return swagger.BodyParameter(**{
        "name": "body",
        "in": "body",
        "schema": swagger.JsonReference({
            "$ref": "#/definitions/{}".format(type_name(name_for(schema))),
        }),
    })


def header_param(name, required=False, param_type="string"):
    """
    Build a header parameter definition.

    """
    return swagger.HeaderParameterSubSchema(**{
        "name": name,
        "in": "header",
        "required": required,
        "type": param_type,
    })


def query_param(name, field):
    """
    Build a query parameter definition.

    """
    parameter = build_parameter(field)
    parameter["name"] = name
    parameter["in"] = "query"
    parameter["required"] = field.required

    return swagger.QueryParameterSubSchema(**parameter)


def path_param(name, ns):
    """
    Build a path parameter definition.

    """
    if ns.identifier_type == "uuid":
        param_type = "string"
        param_format = "uuid"
    elif ns.identifier_type == "int":
        param_type = "integer"
        param_format = None
    else:
        param_type = "string"
        param_format = None

    kwargs = {
        "name": name,
        "in": "path",
        "required": True,
        "type": param_type,
    }
    if param_format:
        kwargs["format"] = param_format
    return swagger.PathParameterSubSchema(**kwargs)


def build_operation(operation, ns, rule, func):
    """
    Build an operation definition.

    """
    swagger_operation = swagger.Operation(
        operationId=operation_name(operation, ns),
        parameters=swagger.ParametersList([
        ]),
        responses=swagger.Responses(),
        tags=[ns.subject_name],
    )

    # custom header parameter
    swagger_operation.parameters.append(
        header_param("X-Response-Skip-Null")
    )

    # path parameters
    swagger_operation.parameters.extend([
        path_param(argument, ns)
        for argument in rule.arguments
    ])

    # query string parameters
    qs_schema = get_qs_schema(func)
    if qs_schema:
        swagger_operation.parameters.extend([
            query_param(name, field)
            for name, field in qs_schema.fields.items()
        ])

    # body parameter
    request_schema = get_request_schema(func)
    if request_schema:
        swagger_operation.parameters.append(
            body_param(request_schema)
        )

    # sort parameters for predictable output
    swagger_operation.parameters.sort(key=lambda parameter: parameter["name"])

    add_responses(swagger_operation, operation, ns, func)
    return swagger_operation


def add_responses(swagger_operation, operation, ns, func):
    """
    Add responses to an operation.

    """
    # default error
    swagger_operation.responses["default"] = build_response(
        description="An error occurred",
        resource=type_name(name_for(ErrorSchema())),
    )

    if getattr(func, "__doc__", None):
        description = func.__doc__.strip().splitlines()[0]
    else:
        description = "{} {}".format(operation.value.name, ns.subject_name)

    if operation in (Operation.Upload, Operation.UploadFor):
        swagger_operation.consumes = [
            "multipart/form-data"
        ]

    # resource request
    request_resource = get_request_schema(func)
    if isinstance(request_resource, str):
        if not hasattr(swagger_operation, "consumes"):
            swagger_operation.consumes = []
        swagger_operation.consumes.append(request_resource)

    # resources response
    response_resource = get_response_schema(func)
    if isinstance(response_resource, str):
        if not hasattr(swagger_operation, "produces"):
            swagger_operation.produces = []
        swagger_operation.produces.append(response_resource)
    elif not response_resource:
        response_code = (
            204
            if operation.value.default_code == 200
            else operation.value.default_code
        )
        swagger_operation.responses[str(response_code)] = build_response(
            description=description,
        )
    else:
        swagger_operation.responses[str(operation.value.default_code)] = build_response(
            description=description,
            resource=response_resource,
        )


def build_response(description, resource=None):
    """
    Build a response definition.

    """
    response = swagger.Response(
        description=description,
    )
    if resource is not None:
        response.schema = swagger.JsonReference({
            "$ref": "#/definitions/{}".format(type_name(name_for(resource))),
        })
    return response
