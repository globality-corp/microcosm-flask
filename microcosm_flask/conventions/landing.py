"""
Landing Page convention.

"""
from distutils import dist
from io import StringIO
from json import dumps
from pkg_resources import DistributionNotFound, get_distribution

from jinja2 import Template

from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.templates.landing import template


def configure_landing(graph):   # noqa: C901

    def get_properties_and_version():
        """
        Parse the properties from the package information

        """
        try:
            distribution = get_distribution(graph.metadata.name)
            metadata_str = distribution.get_metadata(distribution.PKG_INFO)
            package_info = dist.DistributionMetadata()
            package_info.read_pkg_file(StringIO(metadata_str))
            return package_info
        except DistributionNotFound:
            return None

    def get_swagger_versions():
        """
        Finds all swagger conventions that are bound to the graph

        """
        versions = []

        def matches(operation, ns, rule):
            """
            Defines a condition to determine which endpoints are swagger type

            """
            if(ns.subject == graph.config.swagger_convention.name):
                return True
            return False

        for operation, ns, rule, func in iter_endpoints(graph, matches):
            versions.append(ns.version)

        return versions

    def pretty_dict(dict_):
        return dumps(dict_, sort_keys=True, indent=2, separators=(',', ': '))

    def get_env_file_commands(config, conf_key, conf_string=None):
        if conf_string is None:
            conf_string = []
        for key, value in config.items():
            if isinstance(value, dict):
                get_env_file_commands(value, "{}__{}".format(conf_key, key), conf_string)
            else:
                conf_string.append("export {}__{}='{}'".format(conf_key.upper(), key.upper(), value))
        return conf_string

    def get_links(swagger_versions, properties):
        # add links set in config
        links = {key: value for (key, value) in graph.config.landing_convention.get("links", {}).items()}

        # add links for each swagger version
        for swagger_version in swagger_versions:
            links["swagger {}". format(swagger_version)] = "api/{}/swagger".format(swagger_version)

        # add link to home page
        if hasattr(properties, "url"):
            links["home page"] = properties.url

        return links

    @graph.flask.route("/")
    def render_landing_page():
        """
        Render landing page

        """
        config = graph.config_convention.to_dict()
        env = get_env_file_commands(config, graph.metadata.name)
        health = graph.health_convention.to_dict()
        properties = get_properties_and_version()
        swagger_versions = get_swagger_versions()

        return Template(template).render(
            config=pretty_dict(config),
            description=properties.description if properties else None,
            env=env,
            health=pretty_dict(health),
            links=get_links(swagger_versions, properties),
            service_name=graph.metadata.name,
            version=getattr(properties, 'version', None),
        )
