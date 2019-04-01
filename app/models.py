import os
from datetime import datetime

from flask import Flask
from flask.ext.script import Manager, Shell
from flask.ext.login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Sequence, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy import func

from reservationservice.app import db, app

from general.util.db_helper import uuid_generator


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.String(100), primary_key=True, default=uuid_generator)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime)


if __name__ == '__main__':
    manager.run()
