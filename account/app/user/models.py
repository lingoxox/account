import uuid
from oslo_utils import timeutils
from sqlalchemy import (Table, Column, Index, Integer, BigInteger, Enum, String,
                        MetaData, schema, Unicode, text, DECIMAL)
from sqlalchemy import orm
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float, SmallInteger
from account.db.models import BASE, CourseBase, ExptPlatformBase

user_states = ('active', 'locked', 'creating', 'deleting')


# 角色
class Role(BASE, ExptPlatformBase):
    __tablename__ = 'role'
    __table_args__ = (
        Index('role_idx', 'id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True, comment="角色名(唯一)")
    uuid = Column(String(32), nullable=True)
    description = Column(Text, nullable=True, comment="简介")

    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: timeutils.utcnow())
    deleted_at = Column(DateTime, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, comment='是否删除')


# 用户

class User(BASE, ExptPlatformBase):
    __tablename__ = 'user'
    __table_args__ = (
        schema.UniqueConstraint(
            'uuid',
            name="uniq_user0uuid"),

        schema.Index('user_uuid_idx', 'uuid')

    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    uuid = Column(String(32), nullable=False, comment='uuid')
    username = Column(String(255), nullable=False, comment='用户名')
    password = Column(String(128), nullable=False, comment='密码')
    cellphone = Column(String(25), nullable=False, comment='手机号')
    email = Column(String(255), nullable=False, comment='邮箱')
    role_id = Column(Integer, ForeignKey('role.id'), comment='角色id')
    avatar = Column(Text, comment="头像")
    career_id = Column(String(128), comment="学号/工号")
    real_name = Column(String(128), comment="姓名")
    gender = Column(Integer, comment="性别")
    college = Column(String(255), comment="院系")
    specialty = Column(String(255), comment="专业")
    grade_name = Column(String(255), comment="年级")
    school = Column(String(255), comment="学校")
    class_name = Column(String(255), comment="班级")
    state = Column(Enum(*user_states), nullable=False, comment='账户状态')
    last_login = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=True, comment='最后登陆时间')
    login_chance = Column(Integer, nullable=False, default=5, comment='尝试登录次数')
    lock_datetime = Column(DateTime, nullable=True, comment='锁定时间')
    last_retry = Column(DateTime, nullable=True, comment='重试时间')
    ipaddr = Column(String(255), nullable=True, comment='ip地址')
    lock_interval = Column(Integer, nullable=True, default=60 * 30, comment='锁定时长')

    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')
    deleted = Column(Boolean, nullable=False, default=False, comment='是否删除')
    deleted_at = Column(DateTime, comment='删除时间')
    desc = Column(Text, comment="desc")

    def cascade_delete(self, session):
        related_objects = [self.logins]
        for relates in related_objects:
            if isinstance(relates, (list, tuple)):
                for relate in relates:
                    relate.delete(session=session)
            else:
                relates.delete(session=session)


class UserLogin(BASE, ExptPlatformBase):
    __tablename__ = 'user_login'
    __table_args__ = ()

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    location = Column(String(32), comment="地域")
    ipaddr = Column(String(15), comment="登录ip")
    user_uuid = Column(String(32), ForeignKey('user.uuid'))
    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    user = orm.relationship(User,
                            backref=orm.backref('logins'),
                            foreign_keys=user_uuid,
                            primaryjoin=user_uuid == User.uuid)


class UserHistoryTrend(BASE, ExptPlatformBase):
    __tablename__ = 'user_history_trend'
    __table_args__ = ()

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(DateTime, nullable=False, comment="日期")
    active_user = Column(Integer, nullable=False, default=0, comment='登录用户数')
    new_user = Column(Integer, default=0)
    type = Column(Integer, nullable=False)


#  权限
class Permission(BASE, ExptPlatformBase):
    __tablename__ = 'permission'
    __table_args__ = (
        schema.UniqueConstraint(
            'name',
            name="uniq_permission0name"),
    )

    created_at = Column('created_at', DateTime)
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="权限名(中)")
    permission_name = Column(String(255), nullable=False, comment="权限名(英大写)")
    description = Column(Text)


role_permission = Table(
    'role_permission', BASE.metadata,
    Column('role_id', Integer, ForeignKey('role.id'), nullable=False, comment="角色id"),
    Column('permission_id', Integer, ForeignKey('permission.id'), nullable=False, comment="权限id"),
)