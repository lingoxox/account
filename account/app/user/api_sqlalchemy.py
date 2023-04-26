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
from .models import User

from oslo_config import cfg
CONF = cfg.CONF
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _filters_user(filters):

    user_uuid = filters.pop("user_uuid", None)
    username = filters.pop("username", None)
    password = filters.pop("password", None)
    cellphone = filters.pop("cellphone", None)
    email = filters.pop("email", None)
    role_id = filters.pop("role_id", None)
    career_id = filters.pop("career_id", None)
    real_name = filters.pop("real_name", None)
    gender = filters.pop("gender", None)
    college = filters.pop("college", None)
    specialty = filters.pop("specialty", None)
    grade_name = filters.pop("grade_name", None)
    school = filters.pop("school", None)
    class_name = filters.pop("class_name", None)
    state = filters.pop("state", None)
    ipaddr = filters.pop("ipaddr", None)
    deleted = filters.pop("deleted", False)

    keywords = filters.pop("keywords", None)


    user_query = sa_api.get_session().query(User)

    # 默认查询未删除的用户
    if not deleted:
        user_query = user_query.filter(User.deleted == False)
    if user_uuid:
        user_query = user_query.filter(User.uuid == user_uuid)
    if username:
        user_query = user_query.filter(User.username == username)

    if keywords:
        user_query = user_query.filter(
                    or_(User.username.like('%' + keywords + '%'),
                        User.real_name.like('%' + keywords + '%'),
                        User.career_id.like('%' + keywords + '%'),
                        User.email.like('%' + keywords + '%'),
                        User.cellphone.like('%' + keywords + '%')))

    if password:
        user_query = user_query.filter(User.password == password)
    if cellphone:
        user_query = user_query.filter(User.cellphone == cellphone)
    if email:
        user_query = user_query.filter(User.email == email)
    if role_id:
        user_query = user_query.filter(User.role_id == role_id)
    if career_id:
        user_query = user_query.filter(User.career_id == career_id)
    if real_name:
        user_query = user_query.filter(User.real_name == real_name)
    if gender:
        user_query = user_query.filter(User.gender == gender)
    if college:
        user_query = user_query.filter(User.college == college)
    if specialty:
        user_query = user_query.filter(User.specialty == specialty)
    if grade_name:
        user_query = user_query.filter(User.grade_name == grade_name)
    if school:
        user_query = user_query.filter(User.school == school)
    if class_name:
        user_query = user_query.filter(User.class_name == class_name)
    if state:
        user_query = user_query.filter(User.state == state)
    if ipaddr:
        user_query = user_query.filter(User.ipaddr == ipaddr)

    return user_query





def get_user_list(value):

    limit = value.pop("limit", None)
    offset = value.pop("offset", None)

    user_dic = _filters_user(filters=value)

    if limit:
        user_dic = user_dic.limit(limit)

    if offset:
        user_dic = user_dic.offset(offset)

    return user_dic.all()



def get_user_list_count(value):

    user_dic = _filters_user(filters=value)

    return user_dic.count()



def user_create(values):

    user_ref = User.from_dict(json.loads(values.json()))

    print("======user_ref====save===1==", user_ref)
    print("======user_ref====save===2==", user_ref.__dict__)
    try:
        user_ref.save()
    except db_exc.DBDuplicateEntry as e:
        if 'name' in e.columns:
            raise exception.UserNameExistsWithUniversity(name=values.get('username'),
                                                         site_id=values.get('site_id'))
        if 'cellphone' in e.columns:
            raise exception.UserCellPhoneExists(cellphone=values.get('cellphone'))

        import traceback
        traceback.print_exc()
    return user_ref



def get_user_info(user_uuid):
    """
    根据用户的uuid查询用户的相关信息 user_uuid
    """
    filters = {"user_uuid": user_uuid}

    user_dic = _filters_user(filters=filters)

    user_dic = user_dic.all()

    return user_dic


def user_update(user_uuid, values):
    """
    用户数据更新
    """
    values = json.loads(values.json()) if type(values) is not dict else values
    values.pop('user_uuid', None)
    session = sa_api.get_session()
    query_progress = session.query(User)


    try:
        with session.begin():
            user_ref = user_get(user_uuid, session=session)
            old_user_dict = user_ref.to_dict()

            for k in values:
                if k in values and values[k]:
                    old_user_dict[k] = values[k]
            old_user_dict.update(updated_at=now)
            new_user = models.User.from_dict(old_user_dict)

            data = new_user.to_dict()
            query_progress.filter(User.uuid == user_uuid).update(data, synchronize_session=False)

            # for col in models.User.__table__.columns:
            #     if col.name != 'uuid':
            #         setattr(user_ref, col.name, getattr(new_user, col.name))
            # user_ref.save()


    except db_exc.DBDuplicateEntry as e:
        if 'username' in e.columns:
            raise exception.UserNameExists(name=values.get('username'))
    return new_user


def user_get(user_uuid, session=None, use_slave=False, read_deleted='no'):
    query = sa_api.model_query(models.User, session=session,
                        use_slave=use_slave, read_deleted=read_deleted).filter_by(uuid=user_uuid)

    result = query.first()
    if not result:
        raise exception.UserNotFound(user_id=user_uuid)

    return result

def login_get_for_user(str_type, account_str, password=None):
    user_query = sa_api.get_session().query(User)
    if str_type == 'username':
        user_query = user_query.filter(User.username == account_str)
    if str_type == 'cellphone':
        user_query = user_query.filter(User.cellphone == account_str)
    if str_type == 'email':
        user_query = user_query.filter(User.email == account_str)
    user_query = user_query.filter(User.password == password)
    # 只要一个
    return user_query.first()


def user_count():
    """
    用户数
    """
    filters = {}
    user_dic = _filters_user(filters=filters)

    return user_dic.count()


def user_login_create(values):
    user_login_ref = models.UserLogin.from_dict(values)
    user_login_ref.save()
    return user_login_ref

def user_login_destroy(lock_id):
    session = sa_api.get_session()
    with session.begin():
        ref = sa_api.model_query(models.UserLogin, session=session). \
            filter_by(id=lock_id). \
            first()
        if ref:
            session.delete(ref)



def user_login_update_by_user(user_id, values):
    reverse = values.pop('reverse', False)
    if reverse:
        update_dict = {'lock_datetime': values.get('lock_datetime')}
        # login_ip   ==>   admin lock set 'lock_interval': 8640000
        if 'lock_interval' in values and 'login_ip' in values and values.get("login_ip") == "0.0.0.0":
            update_dict['lock_interval'] = values.get('lock_interval')
        user_update(user_id, update_dict)
    elif 'lock_interval' in values:
        user_update(user_id, {'lock_interval': values.get('lock_interval')})

    try:
        refs = user_login_get_by_filters(user_id=user_id)
        if not refs:
            user_login_create(values)
        else:
            sa_api.model_query(models.UserLogin, read_deleted="no"). \
                filter_by(user_id=user_id).update(values)
    except Exception:
        pass


def user_login_get_by_filters(user_id=None, login_ip=None):
    lock_refs = sa_api.model_query(models.UserLogin, read_deleted="no")
    if user_id:
        lock_refs = lock_refs.filter_by(user_id=user_id)
    if login_ip:
        lock_refs = lock_refs.filter_by(login_ip=login_ip)
    return lock_refs.all()



def update_user_for_username(usernamem, values):
    """
    用户数据更新
    """

    session = sa_api.get_session()
    query_progress = session.query(User)
    new_user = query_progress.filter(User.username == usernamem).update(values, synchronize_session=False)

    return new_user
