"""
Example Application
Usage:
    analyst [options]
Options:
    -h --help                   Show this screen.
"""
import sys
import aumbry
from docopt import docopt
from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker

from analyst.app import AnalystService
from analyst.config import AppConfig


class CustomWorker(SyncWorker):
    def handle_quit(self, sig, frame):
        self.app.application.stop(sig)
        super(CustomWorker, self).handle_quit(sig, frame)

    def run(self):
        self.app.application.start()
        super(CustomWorker, self).run()


class GunicornApp(BaseApplication):
    """ Custom Gunicorn application
    This allows for us to load gunicorn settings from an external source
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

        self.cfg.set("worker_class", "analyst.__main__.CustomWorker")

    def load(self):
        return self.application


def main():
    # docopt(__doc__)

    cfg = aumbry.load(
        aumbry.FILE, AppConfig, {"CONFIG_FILE_PATH": "./etc/analyst/config.yml"}
    )

    api_app = AnalystService(cfg)
    gunicorn_app = GunicornApp(api_app, cfg.gunicorn)

    gunicorn_app.run()


if __name__ == "__main__":
    sys.exit(main())
