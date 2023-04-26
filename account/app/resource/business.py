#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import uuid
from oslo_config import cfg

from ...common import exception
from ...common import clean
from ...common.i18n import _

from . import api_sqlalchemy as db_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

def get_resource_list(values):
    resource_list = db_api.get_resource_list(values)
    return resource_list



def get_resource_info(res_type):
    resource_list = db_api.get_resource_info(res_type)
    return resource_list




def update_resource(values):
    resource_list = db_api.update_resource(values)
    return resource_list


