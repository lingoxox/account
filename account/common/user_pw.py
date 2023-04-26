

import collections

from oslo_config import cfg
from oslo_log import log

import passlib.hash


from . import exception
from .i18n import _LW

CONF = cfg.CONF

LOG = log.getLogger(__name__)


def hash_password(password):
    """Hash a password. Hard."""
    password_utf8 = password.encode('utf-8')
    return passlib.hash.sha512_crypt.encrypt(
        password_utf8, rounds=CONF.identity.crypt_strength)

def verify_length_and_trunc_password(password):
    """Verify and truncate the provided password to the max_password_length."""

    max_length = CONF.identity.max_password_length

    try:
        if len(password) > max_length:
            if CONF.strict_password_check:
                raise exception.PasswordVerificationError(size=max_length)
            else:
                LOG.warning(
                    _LW('Truncating user password to '
                        '%d characters.'), max_length)
                return password[:max_length]
        else:
            return password
    except TypeError:
        raise exception.ValidationError(attribute='string', target='password')

def check_password(password, hashed):
    """Check that a plaintext password matches hashed.

    hashpw returns the salt value concatenated with the actual hash value.
    It extracts the actual salt if this value is then passed as the salt.

    """
    if password is None or hashed is None:
        return False
    password_utf8 = verify_length_and_trunc_password(password).encode('utf-8')
    return passlib.hash.sha512_crypt.verify(password_utf8, hashed)