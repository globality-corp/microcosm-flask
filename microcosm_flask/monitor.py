from collections import namedtuple
from datadog import statsd
from flask import request
from functools import wraps
from microcosm.api import defaults
from microcosm_logging.timing import elapsed_time
from microcosm_flask.errors import (
    extract_status_code,
)

from microcosm_flask.audit import parse_response


MonitorOptions = namedtuple("MonitorOptions", [
    "enable_datadog",
    "enable_datadog_testing",
])

class MonitorInfo(object):

    """
    
    Capture the information related to the request we would like to monitor

    """

    def __init__(self, func):
        self.operation = request.endpoint
        self.method = request.method
        self.func = func.__name__
        self.timing = dict()
        self.status_code = None
        self.result = 'unknown';

    def analyze_response(self, response):
        self.result = 'success'
        body, self.status_code = parse_response(response)
        
    def analyze_error(self, error):
        self.result = 'failure'
        self.status_code = extract_status_code(error)
       

DATADOG_METRIC_NAME = "microcosm.flask.requests"

def datadog_send_metric(info, response, is_testing):
    
    # Prepare the datadog tags
    tags = []
    tags.append('operation:'+info.operation)
    tags.append('method:'+info.method)
    tags.append('func:'+info.func)
    tags.append('status_code:'+str(info.status_code))
    tags.append('result:'+info.result)

    # If testing is enabled send the DD tags in a header
    if (is_testing and (response != None)) :
        response.headers[DATADOG_METRIC_NAME] = str(tags)
    
    statsd.histogram(DATADOG_METRIC_NAME, info.timing['elapsed_time']*1000, tags=tags)


def _monitor_request(options, func, *args, **kwargs):
    response = None
    monitor_info = MonitorInfo(func)
    try:
        # process the request
        with elapsed_time(monitor_info.timing):
            response = func(*args, **kwargs)
    except Exception as error:
        monitor_info.analyze_error(error)
        raise
    else:
        monitor_info.analyze_response(response)
        return response
    finally:
        # Send metrics to datadog if its enabled
        if options.enable_datadog:
            datadog_send_metric(monitor_info, response, options.enable_datadog_testing)
        
        


@defaults(
    enable_datadog=True
)

def configure_monitor_decorator(graph):
    """
    Configure the monitor decorator.

    """

    enable_datadog = graph.config.monitor.enable_datadog
    enable_datadog_testing = graph.metadata.testing

    def _monitor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            options = MonitorOptions(
                enable_datadog=enable_datadog,
                enable_datadog_testing=enable_datadog_testing,
            )
            return _monitor_request(options, func, *args, **kwargs)
        return wrapper
    return _monitor
