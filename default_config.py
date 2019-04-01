# DEVELOPMENT CONFIG

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = os.environ.get('RS_DATABASE_URI') or \
    'postgresql://postgres:lending@localhost/reservationservice'

RS_API_URL = os.environ.get('RS_API_URL') or \
    "http://localhost:5430/reservationservice/api/v1.0"
