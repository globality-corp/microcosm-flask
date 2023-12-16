"""
Naming conventions for Swagger definitions.

Intended to play nice with generated code (e.g. with Bravado)

"""

from inflection import camelize, pluralize


def operation_name(operation, ns):
    """
    Convert an operation, obj(s) pair into a swagger operation id.

    For compatability with Bravado, we want to use underscores instead of dots and
    verb-friendly names. Example:

        foo.retrieve       => client.foo.retrieve()
        foo.search_for.bar => client.foo.search_for_bars()

    """
    verb = operation.value.name
    if ns.object_:
        return f"{verb}_{pluralize(ns.object_name)}"
    else:
        return verb


def type_name(name):
    """
    Convert an internal name into a swagger type name.

    For example:

        foo_bar => FooBar

    """
    if name.endswith("_schema"):
        name = name[:-7]
    return camelize(name)
