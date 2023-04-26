import uuid
from oslo_utils import timeutils
from sqlalchemy import (Table, Column, Index, Integer, BigInteger, Enum, String,
                        MetaData, schema, Unicode, text, DECIMAL)
from sqlalchemy import orm
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float, SmallInteger
from account.db.models import BASE, CourseBase, ExptPlatformBase





class Resource(BASE, ExptPlatformBase):
    """Represents a service resource."""

    __tablename__ = 'resource'
    __table_args__ = (
        schema.UniqueConstraint('resource', name='uniq_resource0_resource'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), nullable=False)
    resource = Column(String(255), nullable=False, comment="资源标识")
    name = Column(String(255), nullable=False, comment="资源名")
    description = Column(Text)
    total_quota = Column(DECIMAL(30, 2), default=0, comment="最大配额数")
    used_quota = Column(DECIMAL(30, 2), default=0, comment="已使用配额数")
    unit = Column(String(10), nullable=False, default="default")
    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')


class RoleResourceConfig(BASE, ExptPlatformBase):
    """Represents a resource config."""

    __tablename__ = 'role_resource_config'
    __table_args__ = (
        schema.UniqueConstraint('resource_id',
                         name='uniq_resource_config0resource_id'),
    )
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, comment='角色id')
    type = Column(String(32), nullable=False, comment='角色类型')
    # type_id = Column(String(32), default='')
    default_quota = Column(DECIMAL(30, 2), default=0, comment="默认配额大小")
    max_quota = Column(DECIMAL(30, 2), default=0, comment="最大使用配额")
    
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    resource = orm.relationship(Resource,
                                backref=orm.backref('configs',
                                                    cascade='delete'),
                                foreign_keys=resource_id,
                                primaryjoin=resource_id == Resource.id)
    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')


class UserQuota(BASE, ExptPlatformBase):
    """Represents a user's quota."""

    __tablename__ = 'user_quota'
    __table_args__ = ()
    id = Column(Integer, primary_key=True)
    total = Column(DECIMAL(30, 2), default=0)
    used = Column(DECIMAL(30, 2), default=0, comment="已使用配额数")
    user_uuid = Column(String(32), nullable=False)
    
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    resource = orm.relationship(Resource,
                                backref=orm.backref('quotas',
                                                    cascade='delete'),
                                foreign_keys=resource_id,
                                primaryjoin=resource_id == Resource.id)
    
    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')

class UserQuotaBill(BASE, ExptPlatformBase):
    """Represents a user's quota bill."""

    __tablename__ = 'user_quota_bill'
    __table_args__ = (
        schema.Index('user_quota_id'),
    )
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    total_new = Column(DECIMAL(30, 2), nullable=False, default=0, comment="使用的配额数量")
    state = Column(Integer, nullable=False, default=0)
    error = Column(Text, comment="报错信息")
    user_quota_id = Column(String(32), nullable=False)

    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')
    


class UserQuotaApply(BASE, ExptPlatformBase):
    """Represents a user's quota apply."""

    __tablename__ = 'user_quota_apply'
    __table_args__ = (
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), primary_key=True)
    user_uuid = Column(String(32), index=True)
    reason = Column(Text)
    reply = Column(Text)
    state = Column(Integer, index=True)
    
    deleted = Column(Boolean, nullable=False, default=False, comment='是否删除')
    created_at = Column(DateTime, default=lambda: timeutils.utcnow(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, comment='更新时间')
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')


class UserQuotaApplyItem(BASE, ExptPlatformBase):
    """Represents a user's quota apply item."""

    __tablename__ = 'user_quota_apply_item'
    __table_args__ = (
        schema.UniqueConstraint(
            'apply_id', 'resource_id',
            name='uniq_user_quota_apply_item0apply_id_resource_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    apply_quota = Column(DECIMAL(30, 2), default=0)
    allocated_quota = Column(DECIMAL(30, 2), default=0)
    apply_id = Column(Integer, ForeignKey('user_quota_apply.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))

    apply = orm.relationship(UserQuotaApply,
                             backref=orm.backref('items',
                                                 cascade='delete'),
                             foreign_keys=apply_id,
                             primaryjoin=apply_id == UserQuotaApply.id)

    resource = orm.relationship(Resource,
                                backref=orm.backref('quota_applies',
                                                    cascade='delete'),
                                foreign_keys=resource_id,
                                primaryjoin=resource_id == Resource.id)





