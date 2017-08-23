"""
Cloning resources.

"""
from marshmallow import fields, Schema, post_load


class SubstitutionSchema(Schema):
    fromValue = fields.UUID(required=True, attribute="from_value")
    toValue = fields.UUID(required=True, attribute="to_value")


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
    def flatten(self, obj):
        obj["substitutions"] = {
            item["from_value"]: item["to_value"]
            for item in obj["substitutions"]
        }
