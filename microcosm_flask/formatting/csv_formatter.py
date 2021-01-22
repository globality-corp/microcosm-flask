"""
CSV response formatting.

"""
from csv import QUOTE_MINIMAL, writer
from io import StringIO

from werkzeug import Response
from werkzeug.utils import get_content_type

from microcosm_flask.formatting.base import BaseFormatter
from microcosm_flask.formatting.encoding import UTF_8, UTF_8_SIG


class CSVFormatter(BaseFormatter):

    CONTENT_TYPE = "text/csv"

    @property
    def content_type(self):
        return CSVFormatter.CONTENT_TYPE

    def build_headers(self, headers, **kwargs):
        # TODO: pass in optional filename
        filename = "response.csv"
        headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(filename)

        return headers

    def build_response(self, response_data):
        response = Response(
            self.format(response_data),
            content_type=get_content_type(self.content_type, UTF_8)
        )

        # start the output with U+FEFF BYTE ORDER MARK
        # to signal to Excel to import the text file as UTF-8 rather than a legacy encoding
        response.charset = UTF_8_SIG
        return response

    def get_column_names(self, list_response_data):
        response_fields = list(list_response_data[0].keys())

        column_order = getattr(self.response_schema, "csv_column_order", None)
        if column_order is None:
            # We should still be able to return a CSV even if no column order has been specified
            column_names = response_fields
        else:
            column_names = self.response_schema.csv_column_order

            # The column order be only partially specified
            column_names.extend([field_name for field_name in response_fields if field_name not in column_names])

        return column_names

    def format(self, response_data):
        """
        Make Flask `Response` object, with data returned as a generator for the CSV content
        The CSV is built from JSON-like object (Python `dict` or list of `dicts`)

        """
        if "items" in response_data:
            list_response_data = response_data["items"]
        else:
            list_response_data = [response_data]

        write_column_names = type(list_response_data[0]) not in (tuple, list)

        output = StringIO()
        csv_writer = writer(output, quoting=QUOTE_MINIMAL)

        if write_column_names:
            column_names = self.get_column_names(list_response_data)
            csv_writer.writerow(column_names)

        for item in list_response_data:
            csv_writer.writerow(
                [item[column] for column in column_names] if write_column_names else list(item)
            )

        # Ideally we'd want to `yield` each line to stream the content
        # But something downstream seems to break streaming
        yield output.getvalue()
