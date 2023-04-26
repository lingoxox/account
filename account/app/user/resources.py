import json
from fastapi.responses import JSONResponse

from trit.core.resources import Resource
from trit.core.resources import route, methods_allowed
from . import business as user_business
from . import api_sqlalchemy as user_sql


from fastapi.requests import Request

from .class_info import Item, AllUser, Login


class UsersResource(Resource):
    __endpoint__ = '/user'

    @route('/list')
    def get_user_list(self, request: Request):
        values = request._query_params._dict
        user_list = user_business.get_user_list(values)
        print('self.__endpoint__', self.__endpoint__)
        print('=========request.state.GET=======', request.state)
        return user_list

    @route('/count')
    def get_user_list_count(self, request: Request):
        values = request._query_params._dict
        user_count = user_sql.get_user_list_count(values)
        return user_count


    @route('/create')
    @methods_allowed(methods=['POST'])
    def create_user(self, item: Item):
        user = user_business.create_user(item)
        return user

    @route('/get_info')
    def get_user_info(self, user_uuid):
        user_list = user_business.get_user_info(user_uuid)
        return user_list

    @route('/update')
    @methods_allowed(methods=['POST'])
    def user_update(self, all_user: AllUser):
        user_list = user_business.user_update(all_user)
        return user_list

    @route('/login')
    @methods_allowed(methods=['POST'])
    def user_login(self, request: Request, login: Login):
        host = "127.0.0.1"
        # if request._headers._list and request._headers._list[4][0] == "host":
        #     host = request._headers._list[4][1]


        #  看看ip是不是这个   地域属性还没找到
        host = request.scope['client']

        values = json.loads(request._body)
        values['ipaddr'] = host[0]

        user_list = user_business.user_login(values)
        return user_list

