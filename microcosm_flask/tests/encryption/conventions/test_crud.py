from uuid import uuid4

from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph

import microcosm_flask.tests.encryption.conventions.fixtures.encryptable_controller  # noqa: F401
import microcosm_flask.tests.encryption.conventions.fixtures.encryptable_crud  # noqa: F401
import microcosm_flask.tests.encryption.conventions.fixtures.encryptable_store  # noqa: F401


class TestCRUD:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        self.graph.use(
            "encryptable_crud_routes",
        )
        self.client = self.graph.flask.test_client()

    def assert_response(self, response, status_code, data=None):
        # always validate status code
        assert_that(response.status_code, is_(equal_to(status_code)))

        # expect JSON data except on 204
        if status_code == 204:
            response_data = None
        else:
            response_data = response.json

        # validate data if provided
        if response_data is not None and data is not None:
            assert_that(response_data, is_(equal_to(data)))

    def test_update(self):
        encryptable_id1 = uuid4()
        uri = f"/api/v1/encryptable/{encryptable_id1}"
        request_data = {
            "value": "Chair",
        }
        response = self.client.patch(uri, json=request_data)
        self.assert_response(response, 200, {
            "id": str(encryptable_id1),
            "value": "Chair",
            "otherValue": None,
        })

    def test_update_to_null(self):
        encryptable_id1 = uuid4()
        uri = f"/api/v1/encryptable/{encryptable_id1}"
        request_data = {
            "value": None,
        }
        response = self.client.patch(uri, json=request_data)
        self.assert_response(response, 200, {
            "id": str(encryptable_id1),
            "value": None,
            "otherValue": None,
        })
