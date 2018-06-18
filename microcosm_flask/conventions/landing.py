"""
Landing Page convention.

"""
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.templates.landing import template

from distutils import dist
from io import StringIO
from jinja2 import Template
from pkg_resources import get_distribution, DistributionNotFound


def configure_landing(graph):

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

    @graph.flask.route("/")
    def render_landing_page():
        """
        Render landing page

        """
        properties = get_properties_and_version()
        description = get_description(properties)
        swagger_versions = get_swagger_versions()

        return Template(template).render(
            service_name=graph.metadata.name,
            swagger_versions=swagger_versions,
            description=description,
            homepage=getattr(properties, 'url', None),
            version=getattr(properties, 'version', None),
        )
