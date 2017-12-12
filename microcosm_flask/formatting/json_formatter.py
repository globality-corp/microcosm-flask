from flask import jsonify
from microcosm_flask.formatting.base import BaseFormatter


class JSONFormatter(BaseFormatter):
    def make_response(self, response_data, headers):
        response = jsonify(response_data)
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        return response, headers
