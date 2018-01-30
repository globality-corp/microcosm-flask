from microcosm_flask.formatting.base import BaseFormatter


class TextFormatter(BaseFormatter):

    CONTENT_TYPE = "text/plain"

    @property
    def content_type(self):
        return TextFormatter.CONTENT_TYPE

    def format(self, response_data):
        return response_data
