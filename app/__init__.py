import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'This is a microservice for reservations created by Diego Leon, Jehiel Sanchez, Milton Espinel and MateoSalazar'

app.config.from_object('reservationservice.default_config')

db = SQLAlchemy(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Perform session close and rollback after every request is completed
    :param exception: Exception: optional param that is sent when a exception was raised in the request execution.
    """

    # This is called after a request was been completed.
    # Useful Links:
    # - http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/
    # - http://docs.sqlalchemy.org/en/latest/orm/contextual.html#contextual-thread-local-sessions

    # The session.remove() perform these calls in order:
    # 1. Session.close() on the current Session:
    #  - release any connection/transactional resources owned by the Session first
    #  - discard the Session itself
    #
    # Release a connection means:
    # - that connections are returned to their connection pool
    # - any transactional state is rolled back
    #
    # This prevents error such as:
    # - (sqlalchemy.exc.InvalidRequestError) Can't reconnect until invalid transaction is rolled back
    db.session.remove()
