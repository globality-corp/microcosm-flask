from microcosm_monitoring.monitoring import MonitoringInfo
from flask import request
from microcosm_flask.audit import parse_response
from microcosm_flask.errors import (
    extract_status_code,
)

# Metric used to track execution time per route
MONITORING_METRIC_ROUTE = "microcosm.flask.requests"

class RouteMonitoringInfo(MonitoringInfo):

    """
    Used to collect specific information regarding actions on routes

    """

    def __init__(self, func):
        super().__init__()
        
        super().update_information('operation', '');
        super().update_information('method', '');
        super().update_information('func', func.__name__);
        super().update_information('status_code', None);
        super().update_information('result', 'unknown');
        
    def on_before(self):
        super().update_information('operation', request.endpoint);
        super().update_information('method', request.method);
    
    def on_after(self, response):
        super().update_information('result', 'success');
        body, status_code = parse_response(response)
        super().update_information('status_code', status_code);
    
    def on_error(self, error):
        super().update_information('result', 'failure');
        super().update_information('status_code', extract_status_code(error));


