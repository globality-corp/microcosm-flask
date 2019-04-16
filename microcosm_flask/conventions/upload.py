"""
Conventions for file upload.

"""
from contextlib import ExitStack, contextmanager
from functools import wraps
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from flask import request
from marshmallow import Schema
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import (
    dump_response_data,
    load_query_string_data,
    merge_data,
)
from microcosm_flask.conventions.registry import qs, response
from microcosm_flask.operations import Operation


@contextmanager
def nested(*contexts):
    """
    Reimplementation of nested in python 3.
    """
    with ExitStack() as stack:
        results = [
            stack.enter_context(context)
            for context in contexts
        ]
        yield results


@contextmanager
def temporary_upload(name, fileobj):
    """
    Upload a file to a temporary location.

    Flask will not load sufficiently large files into memory, so it
    makes sense to always load files into a temporary directory.

    """
    tempdir = mkdtemp()
    filename = secure_filename(fileobj.filename)
    filepath = join(tempdir, filename)
    fileobj.save(filepath)
    try:
        yield name, filepath, fileobj.filename
    finally:
        rmtree(tempdir)


class UploadConvention(Convention):

    def __init__(self, graph, exclude_func=None):
        Convention.__init__(self, graph)

        self.exclude_func = exclude_func or (lambda name, fileobj: False)

    def create_upload_func(self, ns, definition, path, operation):
        request_schema = definition.request_schema or Schema()
        response_schema = definition.response_schema or Schema()

        @self.add_route(path, operation, ns)
        @wraps(definition.func)
        def upload(**path_data):
            merged_data = merge_data(request.args.to_dict(), request.form.to_dict())
            request_data = load_query_string_data(request_schema, merged_data)

            if not request.files:
                raise BadRequest("No files were uploaded")

            uploads = [
                temporary_upload(name, fileobj)
                for name, fileobj
                in request.files.items()
                if not self.exclude_func(name, fileobj)
            ]
            with nested(*uploads) as files:
                response_data = definition.func(files, **merge_data(path_data, request_data))
                if response_data is None:
                    return "", 204

            return dump_response_data(response_schema, response_data, operation.value.default_code)

        if definition.request_schema:
            upload = qs(definition.request_schema)(upload)
        if definition.response_schema:
            upload = response(definition.response_schema)(upload)
        return upload

    def configure_upload(self, ns, definition):
        """
        Register an upload endpoint.

        The definition's func should be an upload function, which must:
        - accept kwargs for path data and query string parameters
        - accept a list of tuples of the form (formname, tempfilepath, filename)
        - optionally return a resource

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        upload = self.create_upload_func(ns, definition, ns.collection_path, Operation.Upload)
        upload.__doc__ = "Upload a {}".format(ns.subject_name)

    def configure_uploadfor(self, ns, definition):
        """
        Register an upload-for relation endpoint.

        The definition's func should be an upload function, which must:
        - accept kwargs for path data and query string parameters
        - accept a list of tuples of the form (formname, tempfilepath, filename)
        - optionall return a resource

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        upload_for = self.create_upload_func(ns, definition, ns.relation_path, Operation.UploadFor)
        upload_for.__doc__ = "Upload a {} for a {}".format(ns.subject_name, ns.object_name)


def configure_upload(graph, ns, mappings, exclude_func=None):
    """
    Register Upload endpoints for a resource object.

    """
    convention = UploadConvention(graph, exclude_func)
    convention.configure(ns, mappings)
