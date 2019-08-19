"""
Support for encoding and decoding request/response content.

"""
from flask import request
from inflection import camelize
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import NotFound, UnprocessableEntity

from microcosm_flask.enums import ResponseFormats
from microcosm_flask.naming import name_for


def with_headers(error, headers):
    setattr(error, "headers", headers)
    return error


def with_context(error, errors):
    setattr(error, "context", dict(errors=errors))
    return error


def encode_count_header(count):
    """
    Generate a header for a count HEAD response.

    """
    return {
        "X-Total-Count": count,
    }


def encode_id_header(resource):
    """
    Generate a header for a newly created resource.

    Assume `id` attribute convention.

    """
    if not hasattr(resource, "id"):
        return {}

    return {
        "X-{}-Id".format(
            camelize(name_for(resource))
        ): str(resource.id),
    }


def encode_headers(resource):
    """
    Generate headers from a resource.

    """
    return {}


def load_request_data(request_schema):
    """
    Load request data as JSON using the given schema.

    Forces JSON decoding even if the client not specify the `Content-Type` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 415 errors.

    """
    try:
        json_data = request.get_json(force=True) or {}
    except Exception:
        # if `simplejson` is installed, simplejson.scanner.JSONDecodeError will be raised
        # on malformed JSON, where as built-in `json` returns None
        json_data = {}
    try:
        return request_schema.load(json_data)
    except ValidationError as error:
        raise with_context(
            UnprocessableEntity("Validation error"),
            [
                {
                    "message": "Could not validate field: {}".format(field),
                    "field": field,
                    "reasons": reasons,
                } for field, reasons in error.messages.items()
            ],
        )


def load_query_string_data(request_schema, query_string_data=None):
    """
    Load query string data using the given schema.

    Schemas are assumed to be compatible with the `PageSchema`.

    """
    if query_string_data is None:
        query_string_data = request.args

    try:
        return request_schema.load(query_string_data)
    except ValidationError as error:
        raise with_context(
            UnprocessableEntity("Validation error"),
            error.messages,
        )


def remove_null_values(data):
    if isinstance(data, dict):
        return {
            key: remove_null_values(value)
            for key, value in data.items()
            if value is not None
        }
    if type(data) in (list, tuple):
        return type(data)(map(remove_null_values, data))
    return data


def dump_response_data(response_schema,
                       response_data,
                       status_code=200,
                       headers=None,
                       response_format=None):
    """
    Dumps response data as JSON using the given schema.

    Forces JSON encoding even if the client did not specify the `Accept` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 406 errors.

    """
    if response_schema:
        response_data = response_schema.dump(response_data)

    return make_response(response_data, response_schema, response_format, status_code, headers)


def make_response(response_data,
                  response_schema=None,
                  response_format=None,
                  status_code=200,
                  headers=None,
                  ):

    if response_format is None:
        response_format = ResponseFormats.JSON

    formatter = response_format.value.formatter(response_schema)

    if request.headers.get("X-Response-Skip-Null"):
        # swagger does not currently support null values; remove these conditionally
        response_data = remove_null_values(response_data)

    response = formatter(response_data, headers)
    response.status_code = status_code
    return response


def merge_data(path_data, request_data):
    """
    Merge data from the URI path and the request.

    Path data wins.

    """
    merged = request_data.copy() if request_data else {}
    merged.update(path_data or {})
    return merged


def require_response_data(response_data):
    """
    Enforce that response data is truthy.

    Used to automating 404 errors for CRUD functions that return falsey. Does not
    preclude CRUD functions from raising their own errors.

    :raises NotFound: otherwise

    """
    if not response_data:
        raise NotFound
    return response_data


def find_response_format(allowed_response_formats):
    """
    Basic content negotiation logic.

    If the 'Accept' header doesn't exactly match a format we can handle, we return JSON

    """
    # allowed formats default to [] before this
    if not allowed_response_formats:
        allowed_response_formats = [ResponseFormats.JSON]

    content_type = request.headers.get("Accept")
    if content_type is None:
        # Nothing specified, default to endpoint definition
        if allowed_response_formats:
            return allowed_response_formats[0]
        # Finally, default to JSON
        return ResponseFormats.JSON

    for response_format in ResponseFormats.prioritized():
        if response_format not in allowed_response_formats:
            continue
        if response_format.matches(content_type):
            return response_format

    # fallback for previous behavior
    return ResponseFormats.JSON
