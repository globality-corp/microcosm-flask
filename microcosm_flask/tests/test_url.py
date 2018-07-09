"""
url_extractor_factory tests.

"""
from collections import namedtuple
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)
from microcosm.api import binding, create_object_graph
from werkzeug.routing import BuildError

from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.url import base_url_extractor_factory, url_extractor_factory


class CompanyController:
    def __init__(self, graph):
        self.ns = Namespace(
            subject="company",
            version="v1",
        )
        self.identifier_key = "company_id"

    def retrieve(sel):
        return namedtuple("Company", "id name")("ID", "Name")


@binding("configure_company_v1")
def configure_company(graph):
    ns = Namespace(
        subject="company",
        version="v1",
    )
    mappings = {
        Operation.Create: EndpointDefinition(),
        Operation.Retrieve: EndpointDefinition(),
        Operation.Search: EndpointDefinition(),
    }

    configure_crud(graph, ns, mappings)
    return ns


@binding("configure_user_v1")
def configure_user(graph):
    ns = Namespace(
        subject="user",
        version="v1",
    )
    mappings = {
        Operation.Retrieve: EndpointDefinition(),
    }

    configure_crud(graph, ns, mappings)
    return ns


class TestUriExtractorFactory:

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.graph.use(
            "configure_company_v1",
            "configure_user_v1",
        )
        self.graph.lock()

    def test_default_extractor(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory()
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company/ID"))

    def test_set_operation(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory(operation=Operation.Search)
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company"))

    def test_set_url_string_args(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory(
            name=lambda ctrl, model: model.name,
            limit=lambda ctrl, model: 1,
        )
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company/ID?name=Name&limit=1"))

    def test_identifier_passed_twice(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory(
            company_id=lambda ctrl, model: model.name,
        )
        with self.graph.app.test_request_context():
            assert_that(calling(extractor).with_args(controller, model), raises(TypeError))

    def test_use_model_id_set_to_false(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory(
            use_model_identifier=False,
            company_id=lambda ctrl, model: model.name,
        )
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company/Name"))

    def test_missing_identifier_key(self):
        controller = CompanyController(self.graph)
        controller.identifier_key = None
        model = controller.retrieve()

        extractor = url_extractor_factory()
        with self.graph.app.test_request_context():
            assert_that(calling(extractor).with_args(controller, model), raises(BuildError))

    def test_set_identifier_key(self):
        controller = CompanyController(self.graph)
        controller.identifier_key = None
        model = controller.retrieve()

        extractor = url_extractor_factory(schema_identifier="company_id")
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company/ID"))

    def test_missing_ns(self):
        controller = CompanyController(self.graph)
        controller.ns = None
        model = controller.retrieve()

        extractor = url_extractor_factory()
        with self.graph.app.test_request_context():
            assert_that(calling(extractor).with_args(controller, model), raises(AttributeError))

    def test_set_ns(self):
        controller = CompanyController(self.graph)
        controller.ns = None
        model = controller.retrieve()

        extractor = url_extractor_factory(ns=Namespace(
            subject="company",
            version="v1",
        ))
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company/ID"))

    def test_set_ns_and_identifier_key(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = url_extractor_factory(schema_identifier="user_id", ns=Namespace(subject="user", version="v1"))
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/user/ID"))

    def test_base_extractor(self):
        controller = CompanyController(self.graph)
        model = controller.retrieve()

        extractor = base_url_extractor_factory(
            operation=Operation.Search,
            query_args_extractors=[
                (lambda ctrl, model: model.name, lambda ctrl, model: model.name),
            ],
        )
        with self.graph.app.test_request_context():
            url = extractor(controller, model)
        assert_that(url), is_(equal_to("http://localhost/api/v1/company?Name=Name"))
