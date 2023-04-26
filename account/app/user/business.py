#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2023/4/11 下午11:47"

import uuid
import logging
import datetime
from oslo_config import cfg

from ...common import exception
from ...common import clean
from ...common.i18n import _
from ...common.user_pw import check_password

from account.common.user_pw import hash_password
from . import api_sqlalchemy as db_api

from ..resource import business as res_business


from trit.core.cache import cache
redis_client = cache.client_instance


CONF = cfg.CONF
LOG = logging.getLogger(__name__)
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_user_list(values):
    user_list = db_api.get_user_list(values)
    return user_list


def create_user(user_ref):
    # 系统支持的最大用户数


    sys_max_users =  res_business.get_resource_info('USERS')
    sys_max_users_count = sys_max_users[0]['total_quota'] if sys_max_users else 0

    now_sys_user_count = db_api.user_count()
    if now_sys_user_count >= sys_max_users_count:
        return "Exceeded the maximum number of registrations on the platform"


    user = user_ref.copy()

    if user.username:
        user.username = clean.user_name(user.username)
    else:
        raise exception.ValidationError(_('username field is required'))
    if user.password:
        user.password = clean.user_password(user.password)
    else:
        raise exception.ValidationError(_('password field is required'))

    if not user.role_id:
        raise exception.ValidationError(_('role_id field is required'))

    user.uuid = uuid.uuid4().hex

    if not user.lock_interval:
        user.lock_interval = CONF.identity.lock_interval
    if user.lock_interval <= 0:
        raise exception.ValidationError(
            _('lock_interval field must bigger than zero')
        )

    user.password = hash_password(user.password)

    user_created_info = db_api.user_create(user)

    return user_created_info

def get_user_info(user_uuid):

    info = db_api.get_user_info(user_uuid)

    return info


def user_update(values):
    user_uuid = values.user_uuid
    data = db_api.user_update(user_uuid, values)
    return data


def user_login(values):
    """
    用户登录的三种状态
    state : 0  --  锁定
            1  --  密码错误
            2  --  正确
    """
    ipaddr = values.get('ipaddr', None)
    update_values = {
        "last_retry": now,
        "ipaddr": ipaddr,
    }
    is_right = check_login(values)

    if 'lock' in is_right and is_right['lock']:
        return "Account locked"

    if is_right['state']:
        user_uuid = is_right['user_uuid']
        values['user_uuid'] = user_uuid
        db_api.user_login_create(values)

        update_values.update(last_login=now, state="active")
        db_api.user_update(user_uuid, update_values)
        return "Success"
    else:
        return "Password error!"

def check_login(values):
    account_str = values.get('account_str', None) # 用户输入的用户名/邮箱/手机号
    password = values.get('password', None) # 用户输入的用户名/邮箱/手机号
    ipaddr = values.get('ipaddr', None)

    is_locked_num = redis_client.get(f'lock_{account_str}_addr_{ipaddr}')
    is_locked_num = is_locked_num if is_locked_num else 0

    # 获取这个缓存的剩余时间  前4次及继承这个时间  第五次刷新变成30分钟(1800s)
    # is_locked_time = redis_client.ttl(f'lock_{account_str}_addr_{ipaddr}')

    # 如果该用户名/邮箱/手机号  已经在该IP下尝试了5次 直接锁定
    if int(is_locked_num) == 5:
        return {'lock': True}

    if '@' in account_str:
        str_type = 'email'
    elif account_str.isdigit():
        str_type = 'cellphone'
    else:
        str_type = 'username'

    user_ref = db_api.login_get_for_user(str_type, account_str, password)


    # 账号密码是否正确
    if user_ref:
        redis_client.delete(f'lock_{account_str}_addr_{ipaddr}')
        state = True
        return {'state': state, "user_uuid": user_ref.uuid}
    else:
        lock_times = int(is_locked_num) + 1
        redis_client.set(f'lock_{account_str}_addr_{ipaddr}', int(is_locked_num) + 1, ex=1800)
        state = False

        if lock_times == 5:
            update_values = {
                "last_retry": now,
                "ipaddr": ipaddr,
                "lock_datetime": now,
                "state": "locked",

            }
            db_api.update_user_for_username(account_str, update_values)

        return {'state': state, "login_chance": 5 - int(is_locked_num)}


# 批量处理用户数据
def unlock_user(values):
    account_str = values.get('account_str', None)
    redis_client.delete(*redis_client.keys(f'lock_{account_str}_addr_*'))
    pass