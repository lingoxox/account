# Copyright 2012 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
import six

from . import exception
from .i18n import _

URL_PATTERN = '(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+(' \
              '[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'


def check_length(property_name, value, min_length=1, max_length=64):
    if len(value) < min_length:
        if min_length == 1:
            msg = _("%s cannot be empty.") % property_name
        else:
            msg = (_("%(property_name)s cannot be less than "
                   "%(min_length)s characters.") % dict(
                       property_name=property_name, min_length=min_length))
        raise exception.ValidationError(msg)
    if len(value) > max_length:
        msg = (_("%(property_name)s should not be greater than "
               "%(max_length)s characters.") % dict(
                   property_name=property_name, max_length=max_length))

        raise exception.ValidationError(msg)


def check_type(property_name, value, expected_type, display_expected_type):
    if not isinstance(value, expected_type):
        msg = (_("%(property_name)s is not a "
                 "%(display_expected_type)s") % dict(
                     property_name=property_name,
                     display_expected_type=display_expected_type))
        raise exception.ValidationError(msg)


def check_enabled(property_name, enabled):
    # Allow int and it's subclass bool
    check_type('%s enabled' % property_name, enabled, int, 'boolean')
    return bool(enabled)


def check_name(property_name, name, min_length=1, max_length=64):
    check_type('%s name' % property_name, name, six.string_types,
               'str or unicode')
    name = name.strip()
    check_length('%s name' % property_name, name,
                 min_length=min_length, max_length=max_length)
    return name


def check_url(url):
    m = re.match(URL_PATTERN, url)
    if not m:
        raise exception.ValidationError(_('%(url)s is not a valid url.')
                                        % dict(url=url))
    return url


def strip_dict_key(item):
    keys = item.keys()
    for k in keys:
        if k.strip() != k:
            # Key has white space surrounded, strip it
            v = item.pop(k)
            item[k.strip()] = v


EMAIL_PATTERN = '[^\._-][\w\.-]+@(?:[A-Za-z0-9-_]+\.)+[A-Za-z]+$'
NAME_PATTERN = u"[\u4E00-\u9FA5A-Za-z][\u4E00-\u9FA5A-Za-z0-9_]+"


def check_length(property_name, value, min_length=1, max_length=64):
    if len(value) < min_length:
        if min_length == 1:
            msg = _("%s cannot be empty.") % property_name
        else:
            msg = (_("%(property_name)s cannot be less than "
                   "%(min_length)s characters.") % dict(
                       property_name=property_name, min_length=min_length))
        raise exception.ValidationError(msg)
    if len(value) > max_length:
        msg = (_("%(property_name)s should not be greater than "
               "%(max_length)s characters.") % dict(
                   property_name=property_name, max_length=max_length))

        raise exception.ValidationError(msg)


def check_type(property_name, value, expected_type, display_expected_type):
    if not isinstance(value, expected_type):
        msg = (_("%(property_name)s is not a "
                 "%(display_expected_type)s") % dict(
                     property_name=property_name,
                     display_expected_type=display_expected_type))
        raise exception.ValidationError(msg)


def check_enabled(property_name, enabled):
    # Allow int and it's subclass bool
    check_type('%s enabled' % property_name, enabled, int, 'boolean')
    return bool(enabled)


def check_name(property_name, field_name, name,
               min_length=1, max_length=64, re_pattern=NAME_PATTERN):
    check_type('%s %s' % (property_name, field_name), name, six.string_types,
               'str or unicode')
    name = name.strip()
    check_length('%s %s' % (property_name, field_name), name,
                 min_length=min_length, max_length=max_length)
    if re_pattern:
        p = re.compile(re_pattern)
        p_list = p.findall(name)
        if ''.join(p_list) != name:
            msg = (_('%(property_name)s %(field_name)s is not a valid value. '
                     'character, number, _ are allowd,'
                     ' also starting with character')
                   % dict(
                property_name=property_name, field_name=field_name
            ))
            raise exception.ValidationError(msg)
    return name


def check_email(property_name, email):
    check_type('%s email' % property_name, email, six.string_types,
               'str or unicode')
    email = email.strip()
    check_length('%s email' % property_name, email,
                 min_length=3, max_length=255)
    p = re.compile(EMAIL_PATTERN)
    if not p.match(email):
        msg = (_('%(email)s is not a valid email') % dict(
            email=email
        ))
        raise exception.ValidationError(msg)
    return email


def user_name(name):
    # no limit on username format.
    return check_name('User', 'name', name, max_length=255, re_pattern=None)


def user_realname(real_name):
    return check_name('User', 'real_name', real_name, max_length=255, re_pattern=None)


def user_password(password):
    return check_name("User", 'password', password,
                      min_length=6, max_length=128, re_pattern=None)


def user_enabled(enabled):
    return check_enabled('User', enabled)


def user_email(email):
    return check_email('User', email)


def platform_name(name):
    return check_name('Platform', 'name', name, min_length=2, max_length=100)


def history_ipaddr(ipaddr):
    check_type('User History ipaddr', ipaddr, six.string_types,
               'str or unicode')
    import socket
    try:
        socket.inet_aton(ipaddr)
    except socket.error:
        msg = (_('%(property_name)s %(field_name)s is not a valid value. '
                 'four number between (0, 255), seperated by .')
               % dict(
            property_name='User History', field_name='ipaddr'
        ))
        raise exception.ValidationError(msg)
    return ipaddr