"""
Flask path converters.

"""
from flask_uuid import FlaskUUID


def configure_uuid(graph):
    """
    Register the UUID converter.

    """
    return FlaskUUID(graph.flask)


def str_to_bool(value):
    """
    Convert a string value to boolean.
    Similar to distutils.util.strtobool, it returns an int.
    """
    if str(value).lower() in ('yes', 'true', 't', 'y', '1'):
        return 1
    elif str(value).lower() in ('no', 'false', 'f', 'n', '0'):
        return 0
    raise ValueError(f"Invalid boolean value: {value}")