from microcosm_flask.audit import parse_response
from microcosm_flask.errors import extract_status_code


try:
    from microcosm_metrics.classifier import Classifier
except ImportError:
    raise Exception("Route metrics require 'microcosm-metrics'")


class StatusCodeClassifier(Classifier):
    """
    Label route result/error with its status code.

    """
    def label_result(self, result):
        _, status_code, _ = parse_response(result)
        return self.normalize_status_code(status_code)

    def label_error(self, error):
        status_code = extract_status_code(error)
        return self.normalize_status_code(status_code)

    # Return only the first digit of the status code followed by xx as a string
    # Example: 403 becomes "4xx"
    # This will reduce the cardinality of metrics collected which will reduce cost
    # For detailed status code errors we have logs
    def normalize_status_code(self, status_code: int) -> str:
        return str(status_code)[0] + "xx"
