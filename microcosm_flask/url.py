"""
Url fatories.

"""

from microcosm_flask.operations import Operation, NODE_PATTERN


def url_extractor_factory(ns=None, operation=None, use_model_id=None, identifier_key=None, **url_string_args):
    """
    A factory that creates url extractors.
    url extractor is an (component, model) -> string function that can generates url for relevant resources
    The extractors can component.ns and component.identifier_key to easily generates relevant urls.

    Simple examples:

    class Controller:
        def __init__(self, graph):
            self.ns = Namespace(subject="company")
            self.identifier_key = "company_id"
    controller = Controller()
    company = Company(id="ID", clock=3)

    url_extractor_factory()(ctrl, company) -> '/api/v1/company/ID'
    url_extractor_factory(min_clock=lambda cont, obj: obj.clock)(ctrl, company) -> '/api/v1/company/ID?min_clock=3'

    :ns              - Model namespace. component.ns will get used instead if set to None.
    :operation       - microcosm_flask.operations.Operation, default is Operation.Retrieve
    :url_string_args - Allow to specify query args to use
                       Passed as a dictionary of {arg_name: lambda component, model: action}
                       For example: {
                           company_event_id: lambda component, company_event: company_event.id
                           min_clock: lambda component, company_event: company_event.clock
                        }
    :use_model_id    - Should use model.id to create the url.
                       If is None, will use set to True for node operation (such as Retrieve, unlike Search)
    :identifier_key  - Specify the object "id" schema key
                       Cannot be used if use_model_id is set to false.
                       component.identifier_key will get used instead if set to None.

    """
    operation_ = operation or Operation.Retrieve
    use_model_id_ = use_model_id if use_model_id is not None else operation_.value.pattern == NODE_PATTERN

    if identifier_key and not use_model_id_:
        raise TypeError(f"No need to pass identifier_key if use_model_id is set to false")

    def extract(component, model):
        ns_ = ns or component.ns
        url_params = {key: str(extractor(component, model)) for key, extractor in url_string_args.items()}
        if use_model_id_:
            identifier_key_ = identifier_key or component.identifier_key
            if identifier_key_ in url_params:
                raise TypeError(f"identifier_key is set to alredy set parameter {identifier_key_}")
            url_params[identifier_key_] = model.id

        return ns_.url_for(operation_, **url_params)
    return extract
