#!flask/bin/python

from flask_restful import Api

from reservationservice.app import app
from reservationservice.app.resources.reservation import ReservationAPI

userservice_api = Api(app)

userservice_api.add_resource(
    ReservationAPI,
    '/reservation',
    endpoint='reservation'
)

if __name__ == '__main__':
    app.run()
