#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/26 上午11:21"

import datetime
import json
from sqlalchemy import or_, orm


from trit.db.sqlalchemy import api as sa_api
from oslo_db import exception as db_exc
from . import models
from ...common import exception
from .models import Resource, RoleResourceConfig, UserQuota, UserQuotaBill, UserQuotaApply, UserQuotaApplyItem

from oslo_config import cfg
CONF = cfg.CONF

def get_resource_list(params):
    res_query = sa_api.get_session().query(Resource)
    return res_query.all()


def get_resource_info(res_type):
    """
    查看资源具体信息
    """
    res_query = sa_api.get_session().query(Resource)

    if res_type:
        res_query = res_query.filter(Resource.resource == res_type)

    return res_query.all()


def update_resource(params):
    """
    更新资源信息
    """
    values = json.loads(params.json())

    resource = values.pop('resource', None)

    # query = sa_api.get_session().query(Resource)
    # query.filter(Resource.resource == resource).update(values, synchronize_session=False)


    session = sa_api.get_session()
    query_progress = session.query(Resource)
    with session.begin():
        res_ref = get_resource(resource)
        old_res_dict = res_ref.to_dict()

        for k in values:
            if k in values and values[k]:
                old_res_dict[k] = values[k]
        new_resource = models.Resource.from_dict(old_res_dict)

        data = new_resource.to_dict()
        query_progress.filter(Resource.resource == resource).update(data, synchronize_session=False)

    return True



def get_resource(resource):
    query = sa_api.get_session().query(Resource).filter(Resource.resource == resource)

    result = query.first()
    if not result:
        raise exception.ResourceNotFound(resource=resource)

    return result