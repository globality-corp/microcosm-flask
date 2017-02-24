"""
Conventions for file upload.

"""
from flask import request
from microcosm_flask.conventions.base import Convention
from microcosm_flask.operations import Operation
from werkzeug.exceptions import BadRequest


class UploadConvention(Convention):

    def configure_upload(self, ns, definition):
        """
        Register an upload endpoint.

        The definition's func should be an upload function, which must:
        - accept kwargs for path data
        - accept a dict of files

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.graph.route(ns.collection_path, Operation.Upload, ns)
        def upload(**path_data):
            files = request.files

            if not files:
                raise BadRequest("No files uploaded!")

            definition.func(files, **path_data)
            return "", Operation.Upload.value.default_code

        upload.__doc__ = "Upload a file for: {}".format(ns.subject_name)


def configure_upload(graph, ns, mappings):
    """
    Register Upload endpoints for a resource object.

    """
    convention = UploadConvention(graph)
    convention.configure(ns, mappings)
