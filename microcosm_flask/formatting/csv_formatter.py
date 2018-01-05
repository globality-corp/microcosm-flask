from csv import writer, QUOTE_MINIMAL
from io import StringIO

from flask import Response

from microcosm_flask.formatting.base import BaseFormatter

CSV_CONTENT_TYPE = "text/csv"


class CSVFormatter(BaseFormatter):
    def make_response(self, response_data, headers):
        # TODO: pass in optional filename
        filename = "response.csv"
        headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(filename)
        headers["Content-Type"] = "{}; charset=utf-8".format(CSV_CONTENT_TYPE)

        response = Response(self.csvify(response_data), mimetype=CSV_CONTENT_TYPE)
        return response, headers

    def csvify(self, response_data):
        """
        Make Flask `Response` object, with data returned as a generator for the CSV content
        The CSV is built from JSON-like object (Python `dict` or list of `dicts`)

        """
        if "items" in response_data:
            list_response_data = response_data["items"]
        else:
            list_response_data = [response_data]

        response_fields = list(list_response_data[0].keys())

        column_order = getattr(self.response_schema, "csv_column_order", None)
        if column_order is None:
            # We should still be able to return a CSV even if no column order has been specified
            column_names = response_fields
        else:
            column_names = self.response_schema.csv_column_order
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
