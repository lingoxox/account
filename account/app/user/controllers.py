#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2023/4/11 下午11:47"

import logging
from trit.core.events import event_handler, bus_event_handler

from . import api_sqlalchemy as db_api

LOG = logging.getLogger(__name__)


def index():
    return 'this is index'


def test():
    return 'this is test'


def list_cloud():
    cloud_list = db_api.get_public_cloud_list()
    return cloud_list


@event_handler('order.submit')
def notify_order_event(body, message):
    print('RECEIVED MESSAGE: {0!r}'.format(body))

    LOG.info(body)
    LOG.info(message)


@bus_event_handler('order_submit')
def notify_order_bus_event(body, message):
    print('RECEIVED MESSAGE: {0!r}'.format(body))

    LOG.info(body)
    LOG.info(message)
