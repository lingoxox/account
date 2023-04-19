#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2023/4/18 下午2:12"


from trit.core.resources import Resource
from trit.core.resources import route, methods_allowed


class UserResource(Resource):
    __endpoint__ = '/identity'

    @staticmethod
    def get_user_list(self):
        return 'get_user_list'

    @staticmethod
    @route('/update')
    @methods_allowed(methods=['POST'])
    def update_user_list(self):
        return "update_user_list"
