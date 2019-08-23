"""
Cloning resources.

"""
from marshmallow import (
    Schema,
    fields,
    post_load,
    pre_dump,
)


class EdgeSchema(Schema):
    """
    An edge between UUID node ids.

    """
    fromId = fields.UUID(
        attribute="from_id",
        required=True,
    )
    toId = fields.UUID(
        attribute="to_id",
        required=True,
    )


class SubstitutionSchema(Schema):
    """
    A substitution from one UUID id to another.

    This schema is identical to an Edge currently, but is kept distinct in order
    to support non-UUID substitutions if ever needed.

    """
    fromId = fields.UUID(
        attribute="from_id",
        required=True,
    )
    toId = fields.UUID(
        attribute="to_id",
        required=True,
    )


class DAGSchema(Schema):
    """
    Represents a DAG.

    Nodes should be overridden with a non-raw schema.

    """
    nodes = fields.Nested(
        fields.Raw,
        required=True,
        attribute="nodes_map",
    )
    edges = fields.List(
        fields.Nested(EdgeSchema),
        required=True,
    )
    substitutions = fields.List(
        fields.Nested(SubstitutionSchema),
        missing=[],
        required=False,
    )

    @pre_dump
    def unflatten(self, obj, **kwargs):
        """
        Translate substitutions dictionary into objects.

        """
        obj.substitutions = [
            dict(from_id=key, to_id=value)
            for key, value in getattr(obj, "substitutions", {}).items()
        ]
        return obj


class NewCloneSchema(Schema):
    commit = fields.Boolean(
        missing=True,
        required=False,
    )
    substitutions = fields.List(
        fields.Nested(SubstitutionSchema),
        missing=[],
        required=False,
    )

    @post_load
    def flatten(self, obj, **kwargs):
        """
        Translate substitutions into a dictionary.

        """
        obj["substitutions"] = {
            item["from_id"]: item["to_id"]
            for item in obj["substitutions"]
        }
        return obj


class DAGCloningController:

    def __init__(self, store):
        self.store = store

    def explain(self, **kwargs):
        """
        Return a DAG "explaining" what may be cloned.

        """
        return self.store.explain(**kwargs)

    def clone(self, substitutions, commit=True, **kwargs):
        """
        Clone a DAG, optionally skipping the commit.

        """
        return self.store.clone(substitutions, **kwargs)
