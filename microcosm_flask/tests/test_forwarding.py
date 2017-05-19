"""
Forwarding tests.

"""
from flask import url_for
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict
from six import b


class TestForwarding(object):

    def init(self, loader):
        graph = create_object_graph("test", testing=True, loader=loader)
        graph.use(
            "flask",
            "port_forwarding",
        )

        @graph.app.route("/", endpoint="test")
        def endpoint():
            return url_for("test", _external=True)

        return graph.app.test_client()

    def test_port_forwarding(self):
        loader = load_from_dict()
        client = self.init(loader)
        response = client.get(
            "/",
            headers={
                "X-Forwarded-Port": "8080",
            },
        )

        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.data, is_(equal_to(b("http://localhost:8080/"))))

    def test_host_override(self):
        loader = load_from_dict(
            port_forwarding=dict(
                host="service",
            )
        )
        client = self.init(loader)

        response = client.get(
            "/",
            headers={
                "X-Forwarded-Port": "8080",
            },
        )

        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.data, is_(equal_to(b("http://service/"))))
