"""
Push resource definitions to an output destination.

"""
from json import dumps
from logging import getLogger
from sys import stdout
from urlparse import urljoin

from requests import put
from yaml import safe_dump_all


logger = getLogger("sync.push")


def push_yaml(inputs, destination):
    """
    Write inputs to destination as YAML.

    :param inputs: an iterable of (href, resource) pairs
    :param destination: a writable file-like object

    """
    safe_dump_all(({href: resource} for href, resource in inputs), destination)


def push_json(inputs, base_url):
    """
    Write inputs to remote URL as JSON.

    Future implementations could perform paginated PATCH requests to a collection URI
    if our conventions support it.

    """
    for href, resource in inputs:
        # Skip over links-only (discovery) resources
        if resource.keys() == ["_links"]:
            continue

        # Note that `urljoin` will only use the *base* URL of the destination.
        # If we need more control over URI paths, we'll need to use a different function.
        uri = urljoin(base_url, href)
        push_resource_json(uri, resource)


def push_resource_json(uri, resource):
    """
    Push a single resource as JSON to a URI.

    Assumes that the backend supports a replace/put convention.

    """
    # We don't want to submit links back; they are synthetic
    logger.debug("Pushing resource for {}".format(uri))

    response = put(
        uri,
        data=dumps(resource),
        headers={"Content-Type": "application/json"},
    )
    try:
        response.raise_for_status()
    except:
        logger.warn("Unable to replace {}".format(
            uri,
        ))
        raise


def push(args, inputs):
    """
    Push content to a destination.

    If the destination is "-", YAML is written to stdout.
    If the destination has a http prefix, JSON is written to a URL.
    Otherwise, YAML is written to a local file.

    """
    logger.info("Pushing resources to: {}".format(args.output))

    if args.output == "-":
        push_yaml(inputs, stdout)
    elif args.output.startswith("http"):
        push_json(inputs, args.output)
    else:
        with open(args.output, "w") as file_:
            push_yaml(inputs, file_)