"""
Support for encoding and decoding request/response content.

"""
from flask import jsonify, request
from werkzeug import Headers
from werkzeug.exceptions import NotFound, UnprocessableEntity


def with_headers(error, headers):
    setattr(error, "headers", headers)
    return error


def with_context(error, errors):
    setattr(error, "context", dict(errors=errors))
    return error


def load_request_data(request_schema, partial=False):
    """
    Load request data as JSON using the given schema.

    Forces JSON decoding even if the client not specify the `Content-Type` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 415 errors.

    """
    json_data = request.get_json(force=True) or {}
    request_data = request_schema.load(json_data, partial=partial)
    if request_data.errors:
        # pass the validation errors back in the context
        raise with_context(
            UnprocessableEntity("Validation error"), [{
                "message": "Could not validate field: {}".format(field),
                "field": field,
                "reasons": reasons
            } for field, reasons in request_data.errors.items()],
        )
    return request_data.data


def load_query_string_data(request_schema):
    """
    Load query string data using the given schema.

    Schemas are assumbed to be compatible with the `PageSchema`.

    """
    query_string_data = request.args
    request_data = request_schema.load(query_string_data)
    if request_data.errors:
        # pass the validation errors back in the context
        raise with_context(UnprocessableEntity("Validation error"), dict(errors=request_data.errors))
    return request_data.data


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


def dump_response_data(response_schema, response_data, status_code=200, headers=None):
    """
    Dumps response data as JSON using the given schema.

    Forces JSON encoding even if the client did not specify the `Accept` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 406 errors.

    """
    if response_schema:
        response_data = response_schema.dump(response_data).data

    return make_response(response_data, status_code, headers)


def make_response(response_data, status_code=200, headers=None):
    if request.headers.get("X-Response-Skip-Null"):
        # swagger does not currently support null values; remove these conditionally
        response_data = remove_null_values(response_data)

    response = jsonify(response_data)
    response.headers = Headers(headers or {})
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
