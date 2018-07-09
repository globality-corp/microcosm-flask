"""
Url fatories.

"""
from microcosm_flask.operations import Operation, NODE_PATTERN


def basic_url_extractor_factory(ns=None, operation=Operation.Retrieve, query_args_extractors=None):
    """
    A factory that creates url extractors.
    url extractor is an (component, model) -> string function that can generates url for relevant resources

    Simple examples:

    class Controller:
        def __init__(self, graph):
            self.ns = Namespace(subject="company")
    controller = Controller()
    company = Company(id="ID", clock=3)

    url_extractor_factory(operation=Operation.Search, min_clock=3)(ctrl, company) -> '/api/v1/company?min_clock=3'

    :ns                    - Model namespace. Will use component.ns if ns is unspecified.
    :operation             - microcosm_flask.operations.Operation, default is Operation.Retrieve
                             If the operation is a node operation, an identifier extractor should be passed.
    :query_args_extractors - Allow to specify query args to use. Passed as a list of (key, value) tuples.
                             Both the key and the value can be either strings or string extractors functions:
                             Extractor function is an (lambda component, model: action) function

    """
    def extract(component, model):
        ns_ = ns or component.ns
        if not query_args_extractors:
            return ns_.url_for(operation)
        url_params = dict()
        for extractor_key, extractor_value in query_args_extractors:
            key = str((extractor_key(component, model) if callable(extractor_key) else extractor_key))
            value = str((extractor_value(component, model) if callable(extractor_value) else extractor_value))
            if key in url_params:
                raise TypeError(f"Extractor key {key} is passed more then once")
            url_params[key] = value
        return ns_.url_for(operation, **url_params)
    return extract


def url_extractor_factory(
    ns=None,
    operation=Operation.Retrieve,
    use_model_identifier=None,
    model_identifier="id",
    schema_identifier=None,
    **kwargs
):
    """
    A factory that creates url extractors with id extractor.
    url extractor is an (component, model) -> string function that can generates url for relevant resources

    Simple examples:

    class Controller:
        def __init__(self, graph):
            self.ns = Namespace(subject="company")
            self.identifier_key = "company_id"
    controller = Controller()
    company = Company(id="ID", clock=3)

    url_extractor_factory()(ctrl, company) -> '/api/v1/company/ID'

    :ns                   - Model namespace. component.ns will get used instead if set to None.
    :operation            - microcosm_flask.operations.Operation, default is Operation.Retrieve
    :kwargs               - Allow to specify query args to use
                            Passed as a dictionary of strings or extractors (lambda component, model: action)
                            Extractor Example:
                            * min_clock: lambda component, company_event: company_event.clock
    :use_model_identifier - Should use model.model_identifier to create the url.
                            Default value dpeneds on the operation:
                            True for node operations (True for Retrieve, False for Search)
    :model_identifier     -
    :schema_identifier    - Specify the object "id" schema key
                            Cannot be used if use_model_identifier is set to false.
                            component.identifier_key will get used instead if set to None.


    """
    query_args_extractors = list(kwargs.items())
    if use_model_identifier or (use_model_identifier is None and operation.value.pattern == NODE_PATTERN):
        query_args_extractors.append((
            (schema_identifier if schema_identifier is not None else lambda component, _: component.identifier_key),
            lambda component, model: getattr(model, model_identifier),
        ))

    return basic_url_extractor_factory(ns, operation, query_args_extractors)
