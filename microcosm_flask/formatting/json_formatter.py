from flask import jsonify
from microcosm_flask.formatting.base import BaseFormatter

JSON_CONTENT_TYPE = "application/json"


class JSONFormatter(BaseFormatter):
    def make_response(self, response_data, headers):
        response = jsonify(response_data)
        if "Content-Type" not in headers:
            headers["Content-Type"] = JSON_CONTENT_TYPE
        return response, headers
