"""
Landing Page convention.

"""
from distutils import dist
from io import StringIO
from json import dumps

from jinja2 import Template
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.templates.landing import template
from pkg_resources import DistributionNotFound, get_distribution


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

    def get_description(properties):
        """
        Calculate the description based on the package properties

        """
        if not properties:
            return None

        return '. '.join([
            field
            for field in [properties.description, properties.long_description]
            if field is not None
        ])

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

    @graph.flask.route("/")
    def render_landing_page():
        """
        Render landing page

        """
        properties = get_properties_and_version()
        description = get_description(properties)
        swagger_versions = get_swagger_versions()
        config = graph.config_convention.to_dict()
        health = graph.health_convention.to_dict()
        env = get_env_file_commands(config, graph.metadata.name)

        return Template(template).render(
            config=pretty_dict(config),
            description=description,
            env=env,
            health=pretty_dict(health),
            homepage=getattr(properties, 'url', None),
            service_name=graph.metadata.name,
            swagger_versions=swagger_versions,
            version=getattr(properties, 'version', None),
        )
