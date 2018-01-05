"""
Naming conventions.

"""
from inspect import isclass

from inflection import underscore


def name_for(obj):
    """
    Get a name for something.

    Allows overriding of default names using the `__alias__` attribute.

    """
    if isinstance(obj, str):
        return obj

    cls = obj if isclass(obj) else obj.__class__

    if hasattr(cls, "__alias__"):
        return underscore(cls.__alias__)
    else:
        return underscore(cls.__name__)


def collection_path_for(name):
    """
    Get a path for a collection of things.

    """
    return "/{}".format(
        name_for(name),
    )


def singleton_path_for(name):
    """
    Get a path for a singleton thing.

    """
    return "/{}".format(
        name_for(name),
    )


def instance_path_for(name, identifier_type, identifier_key=None):
    """
    Get a path for thing.

    """
    return "/{}/<{}:{}>".format(
        name_for(name),
        identifier_type,
        identifier_key or "{}_id".format(name_for(name)),
    )


def alias_path_for(name):
    """
    Get a path for an alias to a thing

    """
    return "/{}/<{}_name>".format(
        name_for(name),
        name_for(name),
    )


def relation_path_for(from_name, to_name, identifier_type, identifier_key=None):
    """
    Get a path relating a thing to another.

    """
    return "/{}/<{}:{}>/{}".format(
        name_for(from_name),
        identifier_type,
        identifier_key or "{}_id".format(name_for(from_name)),
        name_for(to_name),
    )
