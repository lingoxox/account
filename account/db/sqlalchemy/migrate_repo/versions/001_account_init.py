import uuid



from oslo_utils import timeutils

from sqlalchemy import (Table, Column, Index, Integer, Enum, String, Float, ForeignKey, Text,
                        MetaData, DateTime, Boolean, SmallInteger, BigInteger)

from sqlalchemy import *

from oslo_utils import timeutils
from datetime import datetime
from sqlalchemy import Column, Integer, MetaData, String, Table, SmallInteger, \
    ForeignKey, DateTime, Boolean, Text, Float, UniqueConstraint, Date, Index, Enum, BigInteger, DECIMAL

user_states = ('active', 'locked', 'creating', 'deleting')

def define_tables(meta):

    # 角色
    role = Table(
        'role', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('deleted_at', DateTime),
        Column('deleted', Integer),
        Column('id', Integer, primary_key=True, nullable=False, comment="主键"),
        Column('name', String(255), nullable=False, comment="角色名(唯一)"),
        Column('uuid', String(32), comment="uuid"),
        Column('description', Text),
        UniqueConstraint('name', 'deleted', 'deleted_at', name='uniq_role0name_deleted_deleted_at'),
        mysql_engine='InnoDB'
    )

    # 用户    INDEX SUOYING
    user = Table('user', meta,
        Column('id', Integer, primary_key=True, autoincrement=True, comment='主键'),
        Column('uuid', String(32), nullable=False, comment='uuid'),
        Column('username', String(255), nullable=False, comment='用户名'),
        Column('password', String(128), nullable=False, comment='密码'),
        Column('cellphone', String(25), nullable=False, comment='手机号'),
        Column('email', String(255), nullable=False, comment='邮箱'),
        Column('role_id', Integer, ForeignKey('role.id'), comment='角色id'),
        Column('avatar', Text, comment="头像"),
        Column('career_id', String(128), comment="学号/工号"),
        Column('real_name', String(128), comment="姓名"),
        Column('gender', Integer, comment="性别"),
        Column('college', String(255), comment="院系"),
        Column('specialty', String(255), comment="专业"),
        Column('grade_name', String(255), comment="年级"),
        Column('school', String(255), comment="学校"),
        Column('class_name', String(255), comment="班级"),
        Column('state', Enum(*user_states), nullable=False, comment='账户状态'),
        Column('last_login', DateTime, default=lambda: timeutils.utcnow(), nullable=True, comment='最后登陆时间'),
        Column('login_chance', Integer, nullable=False, default=5, comment='尝试登录次数'),
        Column('lock_datetime', DateTime, nullable=True, comment='锁定时间'),
        Column('last_retry', DateTime, nullable=True, comment='重试时间'),
        Column('ipaddr', String(255), nullable=True, comment='ip地址'),
        Column('lock_interval', Integer, nullable=True, default=60*30, comment='锁定时长'),
        Column('created_at', DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间'),
        Column('updated_at', DateTime, nullable=True, comment='更新时间'),
        Column('deleted', Boolean, nullable=False, default=False, comment='是否删除'),
        Column('deleted_at', DateTime ,comment='删除时间'),
        Column('desc', Text, comment="desc"),
        UniqueConstraint('name', 'deleted', name='uniq_user0name'),
        UniqueConstraint('uuid', name='uniq_user0uuid'),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    Index('user_uuid_idx', user.c.uuid)


    user_history_trend = Table(
        'user_history_trend', meta,
        Column('id', Integer, primary_key=True, autoincrement=True,  nullable=False),
        Column('date', DateTime, nullable=False, comment="日期"),
        Column('active_user', Integer, nullable=False, default=0),
        Column('new_user', Integer, default=0),
        Column('type', Integer, nullable=False),
        mysql_engine='InnoDB'
    )

    user_login = Table(
        'user_login', meta,
        Column('created_at', DateTime),
        Column('id', Integer, primary_key=True, nullable=False, autoincrement=True),
        Column('location', String(32), comment="地域"),
        Column('ipaddr', String(15), comment="登录ip"),
        Column('user_uuid', String(32), ForeignKey(user.c.uuid)),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # 权限 （角色+菜单）
    permission = Table(
        'permission', meta,
        Column('created_at', DateTime),
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, comment="权限名(中)"),
        Column('permission_name', String(255), nullable=False, comment="权限名(英大写)"),
        Column('description', Text),
        UniqueConstraint('name', name='uniq_permission0name'),
        mysql_engine='InnoDB'
    )

    role_permission = Table(
        'role_permission', meta,
        Column('created_at', DateTime),
        Column('role_id', Integer, ForeignKey('role.id'), nullable=False, comment="角色id"),
        Column('permission_id', Integer, ForeignKey('permission.id'), nullable=False, comment="权限id"),
        UniqueConstraint('permission_id', 'role_id',
                         name='uniq_role_permission0permission_id_role_id'),
        mysql_engine='InnoDB'
    )

    # 配额 总配额
    resource = Table(
        'resource', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('uuid', String(32)),
        Column('resource', String(255), nullable=False, comment="资源标识"),
        Column('name', String(255), nullable=False, comment="资源名"),
        Column('description', Text),
        Column('total_quota', DECIMAL(30, 2), default=0, comment="最大配额数"),
        Column('used_quota', DECIMAL(30, 2), default=0, comment="已使用配额数"),
        Column('unit', String(10), nullable=False, default='default', comment="单位"),
        UniqueConstraint('resource', 'deleted', name='uniq_resource0_resource'),
        mysql_engine='InnoDB'
    )

    role_resource_config = Table(
        'role_resource_config', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('role_id', Integer, ForeignKey('role.id'), nullable=False, comment='角色id'),
        Column('type', String(32), nullable=False, comment='角色类型'),
        # Column('type_id', String(32), nullable=True, default=''),
        Column('default_quota', DECIMAL(30, 2), default=0, comment="默认配额大小"),
        Column('max_quota', DECIMAL(30, 2), default=0, comment="最大使用配额"),
        Column('resource_id', Integer,
               ForeignKey('resource.id'), nullable=False),
        UniqueConstraint('resource_id',
                         name='uniq_resource_config0resource_id'),
        mysql_engine='InnoDB'
    )

    user_quota = Table(
        'user_quota', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('total', DECIMAL(30, 2), default=0),
        Column('used', DECIMAL(30, 2), default=0, comment="已使用配额数"),
        Column('user_uuid', String(32), nullable=False),
        Column('resource_id', Integer,
               ForeignKey('resource.id'), nullable=False),
        UniqueConstraint('user_id', 'resource_id', 'deleted',
                         name='uniq_user_quota0user_id_resource_id'),
        mysql_engine='InnoDB'
    )

    # 用户使用配额时记录
    user_quota_bill = Table(
        'user_quota_bill', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('id', BigInteger, primary_key=True, autoincrement=True),
        Column('total_new', DECIMAL(30, 2), nullable=False, default=0,comment="使用的配额数量"),
        Column('state', Integer, nullable=False, default=0),
        Column('error', Text, comment="报错信息"),
        Column('user_quota_id', String(32), nullable=False),
        mysql_engine='InnoDB'
    )


    #TODO
    user_quota_apply = Table(
        'user_quota_apply', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean, nullable=False, default=False, comment='是否删除'),
        Column('id',Integer, primary_key=True, autoincrement=True),
        Column('uuid', String(32), primary_key=True),
        Column('user_uuid', String(32), index=True),
        Column('reason', Text),
        Column('reply', Text),
        Column('state', Integer, index=True),
        mysql_engine='InnoDB'
    )

    user_quota_apply_item = Table(
        'user_quota_apply_item', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('apply_quota', DECIMAL(30, 2), default=0),
        Column('allocated_quota', DECIMAL(30, 2), default=0),
        Column('apply_id', Integer, ForeignKey('user_quota_apply.id')),
        Column('resource_id', Integer, ForeignKey('resource.id')),
        mysql_engine='InnoDB'
    )




    return [

        role,

        user,

        user_login,
        user_history_trend,

        permission,
        role_permission,

        resource,
        role_resource_config,
        user_quota,
        user_quota_bill,

        user_quota_apply,
        user_quota_apply_item

    ]

def _populate_default_users(user_table):
    i = user_table.insert()
    user_uuid = "d10e49115eb34eae85fdce016f340096"
    i.execute(dict(
        uuid=user_uuid,
        name='admin',
        password=hash_password('CloudLab#%123#'),
        state=0,
        enabled=1,
        deleted=0,
    ))



def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # create all tables
    # Take care on create order for those with FK dependencies
    tables = define_tables(meta)

    for table in tables:
        table.create()

    _populate_default_users(tables[1])

    if migrate_engine.name == "mysql":
        tables = [
            "role",

            "user",

            "user_login",
            "user_history_trend",

            "permission",
            "role_permission",

            "resource",
            "role_resource_config",
            "user_quota",
            "user_quota_bill",

            "user_quota_apply",
            "user_quota_apply_item"
        ]

        migrate_engine.execute("SET foreign_key_checks = 0")
        for table in tables:
            migrate_engine.execute(
                "ALTER TABLE %s CONVERT TO CHARACTER SET utf8" % table)
        migrate_engine.execute("SET foreign_key_checks = 1")
        migrate_engine.execute(
            "ALTER DATABASE %s DEFAULT CHARACTER SET utf8" %
            migrate_engine.url.database)
        migrate_engine.execute("ALTER TABLE %s Engine=InnoDB" % table)

def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = define_tables(meta)
    tables.reverse()
    for table in tables:
        table.drop()
