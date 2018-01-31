"""
Response formatting base class.

"""
from abc import ABCMeta, abstractmethod
from binascii import hexlify
try:
    import spooky
except ImportError:
    spooky = None

from flask import Response
from werkzeug.http import quote_etag
from werkzeug.utils import get_content_type


class BaseFormatter(metaclass=ABCMeta):

    def __init__(self, response_schema=None):
        # Formatting could need the response schema
        # e.g. to specify column ordering in CSV response
        self.response_schema = response_schema

    def __call__(self, response_data, headers=None, **kwargs):
        response = self.build_response(response_data)
        headers = self.build_headers(headers=headers or {}, **kwargs)
        response.headers.extend(headers)
        self.build_etag(response, **kwargs)
        return response

    @property
    @abstractmethod
    def content_type(self):
        pass

    def format(self, response_data):
        return response_data

    def build_response(self, response_data):
        return Response(
            self.format(response_data),
            content_type=get_content_type(self.content_type, Response.charset)
        )

    def build_headers(self, headers, **kwargs):
        return headers

    def build_etag(self, response, include_etag=True, **kwargs):
        """
        Add an etag to the response body.

        Uses spooky where possible because it is empirically fast and well-regarded.

        See: http://blog.reverberate.org/2012/01/state-of-hash-functions-2012.html

        """
        if not include_etag:
            return

        if not spooky:
            # use built-in md5
            response.add_etag()
            return

        # use spooky
        response.headers["ETag"] = quote_etag(
            hexlify(
                spooky.hash128(
                    response.get_data(),
                ).to_bytes(16, "little"),
            ).decode("utf-8"),
        )
