#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-flask"
version = "0.1.0"

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
        "Flask>=0.10.1",
        "Flask-BasicAuth>=0.2.0",
        "microcosm>=0.4.0",
        "microcosm-logging>=0.2.0",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "app = microcosm_flask.factories:configure_flask_app",
            "audit = microcosm_flask.audit:configure_audit_decorator",
            "basic_auth = microcosm_flask.basic_auth:configure_basic_auth_decorator",
            "error_handlers = microcosm_flask.errors:configure_error_handlers",
            "flask = microcosm_flask.factories:configure_flask",
            "health = microcosm_flask.conventions.health:configure_health",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
