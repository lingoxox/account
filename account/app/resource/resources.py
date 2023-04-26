
from trit.core.resources import Resource
from trit.core.resources import route, methods_allowed

from . import business as res_business

from .class_info import QResource
class QuotaResource(Resource):
    __endpoint__ = '/resource'

    @route('/list')
    def resource_list(self):
        values = {}
        resource_list = res_business.get_resource_list(values)
        return resource_list

    @route('/get_resource')
    def get_resource_info(self, type_resource):
        resource_list = res_business.get_resource_info(type_resource)
        return resource_list

    @route('/update')
    @methods_allowed(methods=['POST'])
    def update_resource(self, res: QResource):
        resource = res_business.update_resource(res)
        return resource
