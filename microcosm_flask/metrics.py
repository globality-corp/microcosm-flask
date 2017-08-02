"""
Metrics extensions for routes.

"""
try:
    from microcosm_metrics.classifier import Classifier
except ImportError:
    raise Exception("Route metrics require 'microcosm-metrics'")


from microcosm_flask.audit import parse_response
from microcosm_flask.errors import extract_status_code


class StatusCodeClassifier(Classifier):
    """
    Label route result/error with its status code.

    """
    def label_result(self, result):
        _, status_code, _ = parse_response(result)
        return str(status_code)

    def label_error(self, error):
        status_code = extract_status_code(error)
        return str(status_code)
