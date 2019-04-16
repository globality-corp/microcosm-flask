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
from logging import getLogger
from urllib.parse import unquote

from openapi import model as swagger
from werkzeug.routing import BuildError

from microcosm_flask.conventions.registry import (
    get_qs_schema,
    get_request_schema,
    get_response_schema,
)
from microcosm_flask.errors import ErrorContextSchema, ErrorSchema, SubErrorSchema
from microcosm_flask.naming import name_for
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.api import build_parameter, iter_schemas
from microcosm_flask.swagger.naming import operation_name, type_name


logger = getLogger("microcosm_flask.swagger")


def build_swagger(graph, ns, operations):
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
    try:
        schema.validate()
    except Exception:
        logger.exception("Swagger definition did not validate against swagger schema")
        raise

    return schema


def add_paths(paths, base_path, operations):
    """
    Add paths to swagger.

    """
    for operation, ns, rule, func in operations:
        path = build_path(operation, ns)
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
    for definition_schema in iter_definitions(definitions, operations):
        if definition_schema is None:
            continue
        if isinstance(definition_schema, str):
            continue

        for name, schema in iter_schemas(definition_schema):
            definitions.setdefault(name, swagger.Schema(schema))


def iter_definitions(definitions, operations):
    """
    Generate definitions to be converted to swagger schema.

    """
    # general error schema per errors.py
    for error_schema_class in [ErrorSchema, ErrorContextSchema, SubErrorSchema]:
        yield error_schema_class()

    # add all request and response schemas
    for operation, obj, rule, func in operations:
        yield get_request_schema(func)
        yield get_response_schema(func)


def build_path(operation, ns):
    """
    Build a path URI for an operation.

    """
    try:
        return ns.url_for(operation, _external=False)
    except BuildError as error:
        # we are missing some URI path parameters
        uri_templates = {
            argument: "{{{}}}".format(argument)
            for argument in error.suggested.arguments
        }
        # flask will sometimes try to quote '{' and '}' characters
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


def query_param(name, field, required=False):
    """
    Build a query parameter definition.

    """
    parameter = build_parameter(field)
    parameter["name"] = name
    parameter["in"] = "query"
    parameter["required"] = False

    return swagger.QueryParameterSubSchema(**parameter)


def path_param(name, ns):
    """
    Build a path parameter definition.

    """
    if ns.identifier_type == "uuid":
        param_type = "string"
        param_format = "uuid"
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
