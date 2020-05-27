from dataclasses import dataclass
from os import environ
from typing import Any, Optional
from unittest.mock import MagicMock

from microcosm.decorators import defaults
from microcosm.object_graph import ObjectGraph
from microcosm_logging.decorators import logger


try:
    import sentry_sdk
    from sentry_sdk.utils import BadDsn
except ImportError:
    sentry_sdk = None


@dataclass
class SentryConfig:
    dsn: Optional[str] = None
    enabled: bool = False
    client: Optional[Any] = None


def before_send(event, hint):
    """
    Before sending a event to sentry scrub all values that are non-uuid data from the event
    """
    for exception in event["exception"]["values"]:
        for frame in exception["stacktrace"]["frames"]:
            for var_name, value in frame["vars"].items():
                if var_name in ["self", "cls"]:
                    continue
                elif isinstance(value, str):
                    if value.startswith("<function "):
                        continue
                    elif var_name.endswith("_id"):
                        continue
                frame["vars"][var_name] = "<redacted>"
    return event


@defaults(
    enabled=False,
    dsn=None,  # Data Source Name - should be a url
)
@logger
def configure_sentry(graph: ObjectGraph):
    enabled, dsn, sentry = False, None, None
    if graph.config.sentry_logging.enabled and graph.config.sentry_logging.dsn and sentry_sdk:
        enabled = graph.config.sentry_logging.enabled
        dsn = graph.config.sentry_logging.dsn
        if graph.metadata.testing:
            sentry = MagicMock()
        else:
            try:
                sentry = sentry_sdk.init(
                    graph.config.sentry_logging.dsn,
                    server_name=f"{graph.metadata.name}_api",
                    release=graph.config.build_info_convention.sha1,
                    environment=environ.get("MICROCOSM_ENVIRONMENT") or "undefined",
                    before_send=before_send,
                )
            except BadDsn:
                enabled, dsn, sentry = False, None, None
                configure_sentry.logger.error("Bad DSN value set")
    return SentryConfig(
        dsn=dsn,
        enabled=enabled,
        client=sentry
    )
