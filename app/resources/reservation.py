#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import jsonify
from flask_restful import Resource, reqparse



class ReservationAPI(Resource):

    def get(self):
        """

        """
        params = self.get_params()

        return jsonify({})

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

        """
        params = self.post_params()

        return jsonify({})

    def post_params(self):
        """
        Get params for post action
        """

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='json', required=True)
        parser.add_argument('event_id', type=int, location='json', required=True)

        return parser.parse_args()
