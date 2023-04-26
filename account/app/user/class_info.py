from typing import Union
from pydantic import BaseModel


class Item(BaseModel):

    username: Union[str, None] = None
    password: Union[str, None] = None
    role_id: Union[int, None] = None
    lock_interval: Union[int, None] = None
    uuid: Union[str, None] = None
    # cellphone: Union[str, None] = None
    email: Union[str, None] = None
    state: Union[str, None] = 'active'
    # role: Union[str, None] = None


class AllUser(BaseModel):

    user_uuid: Union[str, None] = None
    username: Union[str, None] = None
    password: Union[str, None] = None
    cellphone: Union[str, None] = None
    email: Union[str, None] = None

    avatar: Union[str, None] = None
    career_id: Union[str, None] = None
    real_name: Union[str, None] = None

    gender: Union[int, None] = None
    college: Union[str, None] = None

    specialty: Union[str, None] = None
    grade_name: Union[str, None] = None

    school: Union[str, None] = None
    class_name: Union[str, None] = None
    state: bool = 'active'
    login_chance: Union[int, None] = None

    ipaddr: Union[str, None] = None
    lock_interval: Union[int, None] = None

    deleted: bool = False

    desc: Union[str, None] = None


class Login(BaseModel):
    # ipaddr: Union[str, None] = None
    # location: Union[str, None] = None
    user_uuid: Union[str, None] = None
    password: Union[str, None] = None
    account_str: Union[str, None] = None
