from flask import Response
from microcosm_flask.formatting.base import BaseFormatter


HTML_CONTENT_TYPE = "text/html"


class HTMLFormatter(BaseFormatter):

    def make_response(self, response_data, headers):
        response = Response(response_data, mimetype=HTML_CONTENT_TYPE)
        return response, headers
