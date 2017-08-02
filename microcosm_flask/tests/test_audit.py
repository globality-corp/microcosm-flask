"""
Audit structure tests.

"""
from logging import DEBUG, NOTSET, getLogger
from uuid import uuid4

from flask import g
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    is_not,
    none,
)
from microcosm.api import create_object_graph
from mock import MagicMock
from werkzeug.exceptions import NotFound

from microcosm_flask.audit import AuditOptions, RequestInfo, logging_levels


def test_func(*args, **kwargs):
    pass


class TestRequestInfo(object):
    """
    Test capturing of request data.

    """
    def setup(self):
        self.graph = create_object_graph("example", testing=True, debug=True)
        self.graph.use(
            "flask",
            "request_context",
        )

        self.graph.flask.route("/")(test_func)

        self.options = AuditOptions(
            include_request_body=True,
            include_response_body=True,
            include_query_string=True,
        )

    def test_base_info(self):
        """
        Every log entry identifies the request.

        """
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",
                ))),
            )

    def test_request_context(self):
        """
        Log entries can include context from headers.

        """
        with self.graph.flask.test_request_context("/", headers={"X-Request-Id": "request-id"}):
            request_info = RequestInfo(self.options, test_func, self.graph.request_context)
            dct = request_info.to_dict()
            request_id = dct.pop("X-Request-Id")
            assert_that(request_id, is_(equal_to("request-id")))
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",
                ))),
            )

    def test_success(self):
        """
        Succeessful responses capture status code.

        """
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_response(MagicMock(
                data="{}",
                status_code=201,
            ))
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    success=True,
                    status_code=201,
                ))),
            )

    def test_error(self):
        """
        Errors responses capture the error

        """
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            try:
                raise NotFound("Not Found")
            except Exception as error:
                request_info.capture_error(error)

            dct = request_info.to_dict()
            # NB: stack trace is hard (and pointless) to compare
            stack_trace = dct.pop("stack_trace")
            assert_that(stack_trace, is_not(none()))
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    success=False,
                    status_code=404,
                    message="Not Found",
                    context=dict(errors=[]),
                ))),
            )

    def test_request_body(self):
        """
        Can capture the request body.

        """
        with self.graph.flask.test_request_context("/", data='{"foo": "bar"}'):
            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_request()
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    request_body=dict(foo="bar"),
                ))),
            )

    def test_request_body_with_field_renaming(self):
        """
        Can capture the request body with field renaming

        """
        with self.graph.flask.test_request_context("/", data='{"foo": "bar"}'):
            g.show_request_fields = dict(foo="baz")

            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_request()
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    request_body=dict(baz="bar"),
                ))),
            )

    def test_request_body_with_field_deletion(self):
        """
        Can capture the request body with fields removed

        """
        with self.graph.flask.test_request_context("/", data='{"foo": "bar", "this": "that"}'):
            g.hide_request_fields = ["foo"]

            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_request()
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    request_body=dict(this="that"),
                ))),
            )

    def test_response_id(self):
        pass

    def test_response_body(self):
        """
        Can capture the response body.

        """
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_response(MagicMock(
                data='{"foo": "bar"}',
                status_code=200,
            ))
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    success=True,
                    status_code=200,
                    response_body=dict(foo="bar"),
                ))),
            )

    def test_response_body_with_field_renaming(self):
        """
        Can capture the response body with field renaming

        """
        with self.graph.flask.test_request_context("/"):
            g.show_response_fields = dict(foo="baz")

            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_response(MagicMock(
                data='{"foo": "bar"}',
                status_code=200,
            ))
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    success=True,
                    status_code=200,
                    response_body=dict(baz="bar"),
                ))),
            )

    def test_response_body_with_field_deletion(self):
        """
        Can capture the response body with fields removed

        """
        with self.graph.flask.test_request_context("/"):
            g.hide_response_fields = ["foo"]

            request_info = RequestInfo(self.options, test_func, None)
            request_info.capture_response(MagicMock(
                data='{"foo": "bar", "this": "that"}',
                status_code=200,
            ))
            dct = request_info.to_dict()
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",

                    success=True,
                    status_code=200,
                    response_body=dict(this="that"),
                ))),
            )

    def test_log_default(self):
        """
        Log at INFO by default.

        """
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)

            logger = MagicMock()
            request_info.log(logger)
            logger.info.assert_called_with(dict(
                operation="test_func",
                method="GET",
                func="test_func",
            ))
            logger.warning.assert_not_called()

    def test_log_query_string(self):
        ref_id = str(uuid4())

        with self.graph.flask.test_request_context("/", query_string=dict(foo=ref_id)):
            request_info = RequestInfo(self.options, test_func, None)

            logger = MagicMock()
            request_info.log(logger)
            logger.info.assert_called_with(dict(
                operation="test_func",
                method="GET",
                func="test_func",
                foo=ref_id
            ))

    def test_log_response_id_header(self):
        new_id = str(uuid4())
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            request_info.response_headers = {"X-FooBar-Id": new_id}

            logger = MagicMock()
            request_info.log(logger)
            logger.info.assert_called_with(dict(
                operation="test_func",
                method="GET",
                func="test_func",
                foo_bar_id=new_id,
            ))

    def test_root_logging_level(self):
        """
        Enable DEBUG logging temporarily.

        """
        assert_that(getLogger().getEffectiveLevel(), is_(equal_to(NOTSET)))
        with self.graph.flask.test_request_context("/", headers={"X-Request-Debug": "true"}):
            with logging_levels():
                assert_that(getLogger().getEffectiveLevel(), is_(equal_to(DEBUG)))
        assert_that(getLogger().getEffectiveLevel(), is_(equal_to(NOTSET)))
