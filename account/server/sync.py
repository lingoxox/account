#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/25 下午4:04"


from trit.core.application import Trit

from account.app.example.resources import UserResource
from account.settings import FILE_OPTIONS


def main():

    app = Trit(title='account-sync',
               conf_options=FILE_OPTIONS)

    app.start(sync=True)

