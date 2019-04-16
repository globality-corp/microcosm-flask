"""
REST APIs for an encryptable

"""
from marshmallow import Schema, fields
from microcosm.api import binding

from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.operations import Operation


class UpdateEncryptableSchema(Schema):
    value = fields.String(allow_none=True)
    otherValue = fields.String(attribute="other_value", allow_none=True)


class EncryptableSchema(Schema):
    id = fields.UUID()
    value = fields.String()
    otherValue = fields.String(attribute="other_value")


@binding("encryptable_crud_routes")
def add_crud(graph):
    controller = graph.encryptable_controller

    mappings = {
        Operation.Update: EndpointDefinition(
            func=controller.update_and_reencrypt,
            request_schema=UpdateEncryptableSchema(),
            response_schema=EncryptableSchema(),
        ),
    }
    configure_crud(graph, controller.ns, mappings)
    return controller.ns
