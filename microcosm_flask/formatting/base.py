from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class BaseFormatter(object):
    def __init__(self, response_schema=None):
        # Formatting could need the response schema
        # e.g. to specify column ordering in CSV response
        self.response_schema = response_schema

    @abstractmethod
    def make_response(self, response_data, headers):
        """
        Build network response object from response data `dict`
        The user can also pass in additional headers

        """
        pass