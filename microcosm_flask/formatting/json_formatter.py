from flask import jsonify

from microcosm_flask.formatting.base import BaseFormatter


class JSONFormatter(BaseFormatter):

    CONTENT_TYPE = "application/json"

    @property
    def content_type(self):
        return JSONFormatter.CONTENT_TYPE

    def build_response(self, response_data):
        return jsonify(response_data)
