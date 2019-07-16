import sys
from datetime import datetime
from os import makedirs
from os.path import exists, expanduser, join

from flask import g


try:
    from pyinstrument import Profiler
except ImportError:
    pass


def default_profile_dir(name):
    return expanduser("~/.{name}/profile".format(name=name))


def enable_profiling(graph):
    if "pyinstrument.profiler" not in sys.modules:
        raise Exception("Profiling requires 'pyinstrument'. Make sure it is installed.")

    profile_dir = graph.config.flask.profile_dir or default_profile_dir(name=graph.metadata.name)
    if not exists(profile_dir):
        makedirs(profile_dir)

    graph.app.config['PROFILE'] = True

    app = graph.flask

    @app.before_request
    def before_request():
        g.profiler = Profiler()
        g.profiler.start()

    @app.after_request
    def after_request(response):
        g.profiler.stop()
        output_html = g.profiler.output_html()

        time_tag = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        profile_path = join(profile_dir, f"profile-{time_tag}.html")
        with open(profile_path, "w") as f:
            f.write(output_html)
        graph.app.logger.info(f"Profile saved into: {profile_path}")

        return response

    graph.app.logger.info(f"*** Profiling is ON, Will save profiling data to directory: {profile_dir}")
