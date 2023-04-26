#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2022/8/25 下午4:04"


from trit.core.application import Trit

from account.settings import FILE_OPTIONS


def main():

    app = Trit(title='account-api',
               conf_options=FILE_OPTIONS)

    from account.app.user.resources import UsersResource
    from account.app.resource.resources import QuotaResource

    app.register(resources_cls=[UsersResource, QuotaResource],
                 with_http=True)


    app.start(http=True)

