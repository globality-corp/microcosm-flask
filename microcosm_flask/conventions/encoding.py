"""
Support for encoding and decoding request/response content.

"""
from csv import writer, QUOTE_MINIMAL

from flask import jsonify, request, Response
from inflection import camelize
from six import StringIO
from werkzeug import Headers
from werkzeug.exceptions import NotFound, UnprocessableEntity

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


def load_request_data(request_schema, partial=False):
    """
    Load request data as JSON using the given schema.

    Forces JSON decoding even if the client not specify the `Content-Type` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 415 errors.

    """
    try:
        json_data = request.get_json(force=True) or {}
    except Exception:
        # if `simplpejson` is installed, simplejson.scanner.JSONDecodeError will be raised
        # on malformed JSON, where as built-in `json` returns None
        json_data = {}
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


def load_query_string_data(request_schema, query_string_data=None):
    """
    Load query string data using the given schema.

    Schemas are assumed to be compatible with the `PageSchema`.

    """
    if query_string_data is None:
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


def dump_response_data(response_schema, response_data, status_code=200, headers=None, response_format=None):
    """
    Dumps response data as JSON using the given schema.

    Forces JSON encoding even if the client did not specify the `Accept` header properly.

    This is friendlier to client and test software, even at the cost of not distinguishing
    HTTP 400 and 406 errors.

    """
    if response_schema:
        response_data = response_schema.dump(response_data).data

    return make_response(response_data, response_schema, status_code, headers, response_format)


def make_csv_response(response_data, response_schema, headers):
    # TODO: pass in optional filename
    filename = "response.csv"
    headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(filename)
    headers["Content-Type"] = "text/csv; charset=utf-8"

    response = Response(csvify(response_data, response_schema), mimetype="text/csv")
    return response, headers


def make_json_response(response_data, headers):
    response = jsonify(response_data)
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    return response, headers


def make_response(response_data, response_schema=None, status_code=200, headers=None, response_format=None):
    if request.headers.get("X-Response-Skip-Null"):
        # swagger does not currently support null values; remove these conditionally
        response_data = remove_null_values(response_data)

    headers = headers or {}
    if response_format == "csv":
        response, headers = make_csv_response(response_data, response_schema, headers)
    else:
        # json by default
        response, headers = make_json_response(response_data, headers)

    response.headers = Headers(headers)
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


def csvify(response_data, response_schema):
    """
    Make Flask `response` object, with data returned as a generator for the CSV content
    The CSV is built from JSON-like object (Python `dict` or list of `dicts`)

    """
    # TODO: determine column ordering with response schema
    if "items" in response_data:
        list_response_data = response_data["items"]
    else:
        list_response_data = [response_data]

    response_fields = list(list_response_data[0].keys())

    column_order = getattr(response_schema, "csv_column_order", None)
    if column_order is None:
        # We should still be able to return a CSV even if no column order has been specified
        column_names = response_fields
    else:
        column_names = response_schema.csv_column_order
        # The column order be only partially specified
        column_names.extend([field_name for field_name in response_fields if field_name not in column_names])

    output = StringIO()
    csv_writer = writer(output, quoting=QUOTE_MINIMAL)
    csv_writer.writerow(column_names)
    for item in list_response_data:
        csv_writer.writerow([item[column] for column in column_names])
    # Ideally we'd want to `yield` each line to stream the content
    # But something downstream seems to break streaming
    yield output.getvalue()
