"""
Landing Page convention.

"""
from microcosm_flask.templates.landing import template
from jinja2 import Template


def configure_landing(graph):

    @graph.flask.route("/")
    def render_landing_page():
        """
        Render landing page

        """
        return Template(template).render(
            service_name=graph.metadata.name,
            swagger_version=graph.config.swagger_convention.version,
            description=graph.config.get('description', None),
            github=graph.config.get('github', None),
        )
