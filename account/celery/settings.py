#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/30 下午6:03"

from oslo_config import cfg
from celery import Celery, platforms
from datetime import timedelta

CONF = cfg.CONF

app = Celery('account',
             broker=CONF.celery.broker,
             # backend=CONF.celery.broker,
             include=['account.celery.tasks'])

# 时区设置
app.conf.timezone = "Asia/Shanghai"

platforms.C_FORCE_ROOT = True

app.conf.beat_schedule = {

    'sync_vendor_aliyun_ecs_status': {
        # 指定要执行的任务函数
        'task': 'account.celery.tasks.sync_vendor_aliyun_ecs_status',
        # 设置定时启动的频率,每15s执行一次任务函数
        'schedule': timedelta(seconds=15)
    },

}



