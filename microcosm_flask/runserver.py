"""
Support running the development server.

"""
from argparse import ArgumentParser

from microcosm_flask.profiling import enable_profiling


def parse_args(graph):
    default_port = graph.config.flask.port
    default_enable_profiling = graph.config.flask.enable_profiling

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=default_port)
    parser.add_argument("--with-profiling", action="store_true", default=default_enable_profiling)
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()


def main(graph):
    args = parse_args(graph)

    if args.with_profiling:
        enable_profiling(graph)

    if args.debug:
        graph.metadata.debug = True

    try:
        graph.flask.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        pass
