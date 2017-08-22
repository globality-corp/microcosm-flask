from os import makedirs
from os.path import exists, expanduser

from werkzeug.contrib.profiler import ProfilerMiddleware


def default_profile_dir(name):
    return expanduser("~/.{name}/profile".format(name=name))


def enable_profiling(graph):
    profile_dir = graph.config.flask.profile_dir or default_profile_dir(name=graph.metadata.name)
    if not exists(profile_dir):
        makedirs(profile_dir)

    graph.app.config['PROFILE'] = True
    graph.app.wsgi_app = ProfilerMiddleware(
        graph.app.wsgi_app,
        profile_dir=profile_dir,
    )

    graph.app.logger.info("*** Profiling is ON, Will save profiling data to directory: {}".format(profile_dir))
