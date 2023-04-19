#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/26 上午11:21"

from trit.db.sqlalchemy import api as sa_api

from . import models


def get_public_cloud_list():
    data = sa_api.get_session().query(models.PublicCloud).all()
    return data
