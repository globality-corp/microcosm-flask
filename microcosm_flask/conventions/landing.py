"""
Landing Page convention.

"""
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.templates.landing import template
from jinja2 import Template
from os.path import join
from pkg_resources import working_set, Requirement


def configure_landing(graph):

    def get_properties():
        """
        Parse the properties from the package information

        """
        package = working_set.find(Requirement.parse(graph.metadata.name))
        if not package:
            return dict()
        package_info = open(join(package.egg_info, 'PKG-INFO')).read().splitlines()
        return dict(
            info.split(": ")
            for info in package_info
        )

    def get_description(properties):
        """
        Calculate the description based on the package properties

        """
        if not properties:
            return None

        return '. '.join([
            field
            for field in [properties["Summary"], properties["Description"]]
            if field != "UNKNOWN"
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
        properties = get_properties()
        description = get_description(properties)
        swagger_versions = get_swagger_versions()

        return Template(template).render(
            service_name=graph.metadata.name,
            swagger_versions=swagger_versions,
            description=description,
            github=properties.get("Home-page"),
            version=properties.get("Version"),
        )
