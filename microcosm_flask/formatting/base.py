from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class BaseFormatter(object):

    @abstractmethod
    def make_response(self, response_data, headers):
        """
        Build network response object from response data `dict`
        The user can also pass in additional headers

        """
        pass
