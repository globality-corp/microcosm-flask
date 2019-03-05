from hamcrest import assert_that, calling, raises
from marshmallow import Schema
from microcosm.api import create_object_graph

from microcosm_flask.conventions.base import EndpointDefinition, RouteAlreadyRegisteredException
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class TestCreateCollectionConflict:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

        self.ns = Namespace(subject="foo")
        self.client = self.graph.flask.test_client()

    def test_register_both_create_and_create_collection(self):
        mappings = {
            Operation.Create: EndpointDefinition(
                func=lambda x: x,
                request_schema=Schema(),
                response_schema=Schema(),
            ),
            Operation.CreateCollection: EndpointDefinition(
                func=lambda x: x,
                request_schema=Schema(),
                response_schema=Schema(),
            ),
        }

        assert_that(
            calling(configure_crud).with_args(self.graph, self.ns, mappings),
            raises(RouteAlreadyRegisteredException),
        )
