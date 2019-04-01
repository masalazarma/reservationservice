#!flask/bin/python
import os
import rollbar
import rollbar.contrib.flask
import sys

from flask import got_request_exception
from flask.ext.script import Server, Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy

from reservationservice.app import app, models, api

reload(sys)
sys.setdefaultencoding('utf-8')

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/reservationservice'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(port=5430, use_debugger=True, use_reloader=True))


@app.before_first_request
def init_rollbar():
    """init rollbar module"""

    environment = os.environ.get('ENVIRONMENT')
    if environment == None or environment == 'Development':
        return

    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        app.config['ROLLBAR_API_KEY'],
        # environment name
        environment,
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


if __name__ == '__main__':
    manager.run()
