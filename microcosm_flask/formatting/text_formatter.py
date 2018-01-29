from flask import Response
from microcosm_flask.formatting.base import BaseFormatter


TEXT_CONTENT_TYPE = "text/plain"


class TextFormatter(BaseFormatter):

    def make_response(self, response_data, headers):
        response = Response(response_data, mimetype=TEXT_CONTENT_TYPE)
        return response, headers
