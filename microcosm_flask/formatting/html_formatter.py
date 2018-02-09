from microcosm_flask.formatting.base import BaseFormatter


class HTMLFormatter(BaseFormatter):

    CONTENT_TYPE = "text/html"

    @property
    def content_type(self):
        return HTMLFormatter.CONTENT_TYPE

    def format(self, response_data):
        return response_data
