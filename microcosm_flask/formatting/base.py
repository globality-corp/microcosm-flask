"""
Response formatting base class.

"""
from abc import ABCMeta, abstractmethod

from flask import Response
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
