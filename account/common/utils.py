""" Utils helper """
import collections
from oslo_utils import strutils
from oslo_config import cfg
from oslo_log import log
from oslo_serialization import jsonutils
import passlib.hash
import six
import requests

from decimal import Decimal


CONF = cfg.CONF
LOG = log.getLogger(__name__)


def flatten_dict(d, parent_key=''):
    """Flatten a nested dictionary

    Converts a dictionary with nested values to a single level flat
    dictionary, with dotted notation for each key.

    """
    items = []
    for k, v in d.items():
        new_key = parent_key + '.' + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(list(flatten_dict(v, new_key).items()))
        else:
            items.append((new_key, v))
    return dict(items)


class SmarterEncoder(jsonutils.json.JSONEncoder):
    """Help for JSON encoding dict-like objects."""

    def default(self, obj):
        if not isinstance(obj, dict) and hasattr(obj, 'iteritems'):
            return dict(six.iteritems(obj))

        if isinstance(obj, Decimal):

            float_val = float(obj)
            int_val = int(obj)

            return int_val if float_val == int_val else float_val

        return super(SmarterEncoder, self).default(obj)


def filter_model_result(ref):
    # ref.pop('deleted', None)
    ref.pop('deleted_at', None)


def attr_as_boolean(val_attr):
    """Returns the boolean value, decoded from a string.

    We test explicitly for a value meaning False, which can be one of
    several formats as specified in oslo strutils.FALSE_STRINGS.
    All other string values (including an empty string) are treated as
    meaning True.

    """
    return strutils.bool_from_string(val_attr, default=True)




def notify_third_user_expt_success(third_user_id, cur_uuid, course_uuid):
    headers = {'Content-Type': 'application/json'}
    url = "https://bizwebcast.intel.cn/dev_api/api/CourseExperimenta/UpdateExpLog"
    params = {
        "user_id": third_user_id,
        "cur_uuid": cur_uuid,
        "course_uuid": course_uuid,
        "exp_resu": "ok"
    }

    try:
        res = requests.post(url, json=params, headers=headers)
    except Exception:
        import traceback
        traceback.print_exc()
        res = requests.post(url, json=params, headers=headers)

    print("result", res)
    print("*******************************************to third expt, {} {} {}".format(third_user_id, cur_uuid, course_uuid))
