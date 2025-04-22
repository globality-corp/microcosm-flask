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
    Similar to distutils.util.strtobool but returns a boolean instead of an int.
    """
    if isinstance(value, bool):
        return value
    if str(value).lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif str(value).lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise ValueError(f"Invalid boolean value: {value}")