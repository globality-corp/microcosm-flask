#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-flask"
version = "1.23.0"


setup(
    name=project,
    version=version,
    description="Opinionated persistence with FlaskQL",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-flask",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "Flask>=1.0.2",
        "Flask-BasicAuth>=0.2.0",
        "Flask-Cors>=3.0.7",
        "Flask-UUID>=0.2",
        "marshmallow>=2.18.1",
        "microcosm>=2.6.0",
        "microcosm-logging>=1.5.0",
        "openapi>=1.1.0",
        "python-dateutil>=2.7.3",
        "PyYAML>=3.13",
        "rfc3986>=1.2.0",
    ],
    extras_require={
        "metrics": "microcosm-metrics>=2.2.0",
        "spooky": "spooky>=2.0.0",
    },
    setup_requires=[
        "nose>=1.3.7",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm_flask.swagger.parameters": [
            "decorated = microcosm_flask.swagger.parameters.decorated:DecoratedParameterBuilder",
            "enum = microcosm_flask.swagger.parameters.enum:EnumParameterBuilder",
            "list = microcosm_flask.swagger.parameters.list:ListParameterBuilder",
            "nested = microcosm_flask.swagger.parameters.nested:NestedParameterBuilder",
            "numeric = microcosm_flask.swagger.parameters.numeric:NumericParameterBuilder",
            "timestamp = microcosm_flask.swagger.parameters.timestamp:TimestampParameterBuilder",
        ],
        "microcosm.factories": [
            "app = microcosm_flask.factories:configure_flask_app",
            "audit = microcosm_flask.audit:configure_audit_decorator",
            "basic_auth = microcosm_flask.basic_auth:configure_basic_auth_decorator",
            "build_info_convention = microcosm_flask.conventions.build_info:configure_build_info",
            "build_route_path = microcosm_flask.paths:RoutePathBuilder",
            "discovery_convention = microcosm_flask.conventions.discovery:configure_discovery",
            "error_handlers = microcosm_flask.errors:configure_error_handlers",
            "flask = microcosm_flask.factories:configure_flask",
            "health_convention = microcosm_flask.conventions.health:configure_health",
            "config_convention = microcosm_flask.conventions.config:configure_config",
            "landing_convention = microcosm_flask.conventions.landing:configure_landing",
            "logging_level_convention = microcosm_flask.conventions.logging_level:configure_logging_level",
            "port_forwarding = microcosm_flask.forwarding:configure_port_forwarding",
            "route = microcosm_flask.routing:configure_route_decorator",
            "route_metrics = microcosm_flask.metrics:RouteMetrics",
            "swagger_convention = microcosm_flask.conventions.swagger:configure_swagger",
            "uuid = microcosm_flask.converters:configure_uuid",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.9.0",
    ],
)
