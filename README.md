# microcosm-flask

Opinionated Flask services.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-flask/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-flask/tree/develop)


## Conventions

 - Classify API endpoints according to an enumerated set of operations with well-defined naming conventions
 - Handle errors consistently using a top-level error and nested sub-errrors
 - Handle UUIDs as route path keys
 - Protect endpoints with basic auth
 - Use HAL JSON links to related resources to each other
 - Use Swagger to publish endpoints for interoperability
 - Automate generation of endpoints according to conventions:
    - A health check API endpoint exposes service health
    - RESTful endpoints provide CRUD operations on resources
    - RESTful endpoints allows one resource to be related to another
    - API discovery endpoints allow resource data to be discovered/spidered
    - Swagger endpoints allow endpoint integration to be automated

## Setup

Create a virtualenv

```
mkvirtualenv microcosm-flask
```

Install dependencies

```
pip install -U -e .
```

## Tests

Run the tests

```
pytest
```

## Linting

Lint the code:

```shell
NAME=microcosm_flask ./entrypoint.sh lint
NAME=microcosm_flask ./entrypoint.sh typehinting
```


## Configuration

 - The object graph's `debug` and `testing` flags are propagated to the Flask application
