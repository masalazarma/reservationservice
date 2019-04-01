#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import jsonify
from flask_restful import Resource, reqparse

from reservationservice.app.controllers.reservation import ReservationController

class ReservationAPI(Resource):

    def get(self):
        """
        Get all reservetions by filters
        """
        params = self.get_params()
        reservations = ReservationController().select_reservation(params)

        return jsonify({'data': reservations})

    def get_params(self):
        """
        Get params for get action
        """

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args')
        parser.add_argument('event_id', type=int, location='args')

        return parser.parse_args()

    def post(self):
        """
        Create reservation
        """
        params = self.post_params()
        reservations = ReservationController().create_reservation(params)
        return jsonify({})

    def post_params(self):
        """
        Get params for post action
        """

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='json', required=True)
        parser.add_argument('event_id', type=int, location='json', required=True)

        return parser.parse_args()
