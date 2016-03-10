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
    if isinstance(obj, basestring):
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
    return "/{}".format(name_for(name))


def singleton_path_for(name):
    """
    Get a path for a singleton thing.

    """
    return "/{}".format(name_for(name))


def instance_path_for(name):
    """
    Get a path for thing.

    """
    return "/{}/<uuid(strict=False):{}_id>".format(name_for(name), name)


def relation_path_for(name, relation):
    """
    Get a path relating a thing to another.

    """
    return "/{}/<uuid(strict=False):{}_id>/{}".format(name_for(name), name, relation)
