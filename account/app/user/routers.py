#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/26 下午2:00"


from trit.core.resources.router import BaseAPIRouters
from fastapi.routing import APIRoute as Route

from . import controllers


class APIRouters(BaseAPIRouters):

    def _init_sub_path(self):
        self.sub_path = '/examples'

    def _init_routes(self):
        self.routes = [
            Route(path='/', endpoint=controllers.index, methods=['GET']),
            Route(path='/test', endpoint=controllers.test, methods=['GET', 'POST']),
            Route(path='/list', endpoint=controllers.list_cloud, methods=['GET', 'POST']),
        ]
