#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/30 下午5:44"

import importlib
import logging
from celery import shared_task


LOG = logging.getLogger(__name__)


@shared_task
def sync_vendor_aliyun_ecs_status():

    LOG.info('-------------------sync_vendor_aliyun_ecs_status-------------------')


