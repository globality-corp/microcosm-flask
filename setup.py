#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-flask"
version = "1.6.0"

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
    keywords="microcosm",
    install_requires=[
        "enum34>=1.1.6",
        "Flask>=0.2.12",
        "Flask-BasicAuth>=0.2.0",
        "Flask-Cors>=3.0.3",
        "Flask-UUID>=0.2",
        "marshmallow>=2.15.0",
        "microcosm>=2.4.0",
        "microcosm-logging>=1.0.0",
        "openapi>=1.0.0",
        "python-dateutil>=2.6.1",
        "PyYAML>=3.12",
        "rfc3986>=1.1.0",
    ],
    extras_require={
        "metrics": "microcosm-metrics>=1.0.0",
        "spooky": "spooky>=2.0.0",
    },
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "compare-resources = microcosm_flask.sync.compare:main",
            "sync-resources = microcosm_flask.sync.main:main",
        ],
        "microcosm.factories": [
            "app = microcosm_flask.factories:configure_flask_app",
            "audit = microcosm_flask.audit:configure_audit_decorator",
            "basic_auth = microcosm_flask.basic_auth:configure_basic_auth_decorator",
            "build_info_convention = microcosm_flask.conventions.build_info:configure_build_info",
            "discovery_convention = microcosm_flask.conventions.discovery:configure_discovery",
            "error_handlers = microcosm_flask.errors:configure_error_handlers",
            "flask = microcosm_flask.factories:configure_flask",
            "health_convention = microcosm_flask.conventions.health:configure_health",
            "config_convention = microcosm_flask.conventions.config:configure_config",
            "logging_level_convention = microcosm_flask.conventions.logging_level:configure_logging_level",
            "port_forwarding = microcosm_flask.forwarding:configure_port_forwarding",
            "request_context = microcosm_flask.context:configure_request_context",
            "route = microcosm_flask.routing:configure_route_decorator",
            "swagger_convention = microcosm_flask.conventions.swagger:configure_swagger",
            "uuid = microcosm_flask.converters:configure_uuid",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
