# coding:utf-8
"""account base exception handling.

Includes decorator for re-raising account-type exceptions.

SHOULD include dedicated exception logging.

"""

import functools

from oslo_log import log as logging
from oslo_utils import excutils
import six

from .safe_utils import getcallargs
from .i18n import _
from .i18n import _LE

import webob.exc

LOG = logging.getLogger(__name__)


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init__(self, code=0, title="", explanation=""):
        self.code = code
        self.title = title
        self.explanation = explanation
        super(ConvertedException, self).__init__()


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return {k: v for k, v in six.iteritems(original) if "_pass" not in k}


def wrap_exception(notifier=None, get_notifier=None):
    """This decorator wraps a method to catch any exceptions that may
    get thrown. It also optionally sends the exception to the notification
    system.
    """
    def inner(f):
        def wrapped(self, context, *args, **kw):
            # Don't store self or context in the payload, it now seems to
            # contain confidential information.
            try:
                return f(self, context, *args, **kw)
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    if notifier or get_notifier:
                        payload = dict(exception=e)
                        call_dict = getcallargs(f, context,
                                                           *args, **kw)
                        cleansed = _cleanse_dict(call_dict)
                        payload.update({'args': cleansed})

                        # If f has multiple decorators, they must use
                        # functools.wraps to ensure the name is
                        # propagated.
                        event_type = f.__name__

                        (notifier or get_notifier()).error(context,
                                                           event_type,
                                                           payload)

        return functools.wraps(f)(wrapped)
    return inner


class Error(Exception):
    """Base account Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    msg_fmt = _("An unknown exception occurred.")
    code = 500
    errno = 20000 
    title = 'Internal Server Error'
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs

            except Exception:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))    # noqa

                # at least get the core message out if something happened
                message = self.msg_fmt

        super(Error, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full terraException message, (see __init__)
        return self.args[0]


class EncryptionFailure(Error):
    msg_fmt = _("Failed to encrypt text: %(reason)s")


class DecryptionFailure(Error):
    msg_fmt = _("Failed to decrypt text: %(reason)s")


class RevokeCertFailure(Error):
    msg_fmt = _("Failed to revoke certificate for %(project_id)s")


class Forbidden(Error):
    ec2_code = 'AuthFailure'
    msg_fmt = _("Not authorized.")
    code = 401
    

class NoPermission(Error):
    ec2_code = 'NoPermission'
    msg_fmt = _("Don't have permission: %(perm)s.")
    code = 403


class Invalid(Error):
    msg_fmt = _("Unacceptable parameters.")
    code = 400
    title = 'Bad Request'


class NotFound(Error):
    msg_fmt = _("Resource could not be found.")
    code = 404
    title = 'Not Found'


class Conflict(Error):
    msg_fmt = _("Resource conflict with existed one.")
    code = 409
    title = 'Conflict'


class ResourceNotEnough(Error):
    errno = 20050
    code = 410
    msg_fmt = _(u"%(resources)s")
    title = 'Resource Not Enough'

class InternalServerError(Error):
    ec2_code = 'InternalServerError'
    msg_fmt = "%(err)s"
    code = 411


class NotAvailable(Error):
    ec2_code = 'NotAvailable'
    msg_fmt = "%(err)s"
    code = 414


class InvalidAttribute(Invalid):
    msg_fmt = _("Attribute not supported: %(attr)s")


class ValidationError(Invalid):
    msg_fmt = _("Expecting to find %(attribute)s in %(target)s -"
                " the server could not comply with the request"
                " since it is either malformed or otherwise"
                " incorrect. The client is assumed to be in error.")


class InvalidRequest(Invalid):
    msg_fmt = _("The request is invalid.")


class InvalidResponse(Invalid):
    msg_fmt = _("The response is invalid.")


class InvalidInput(Invalid):
    msg_fmt = _("Invalid input received: %(reason)s")


class InvalidIpProtocol(Invalid):
    msg_fmt = _("Invalid IP protocol %(protocol)s.")


class InvalidContentType(Invalid):
    msg_fmt = _("Invalid content type %(content_type)s.")


class InvalidUnicodeParameter(Invalid):
    msg_fmt = _("Invalid Parameter: "
                "Unicode is not supported by the current database.")


class InvalidAPIVersionString(Invalid):
    msg_fmt = _("API Version String %(version)s is of invalid format. Must "
                "be of format MajorNum.MinorNum.")


class VersionNotFoundForAPIMethod(NotFound):
    msg_fmt = _("API version %(version)s is not supported on this method.")


class InvalidGlobalAPIVersion(Invalid):
    msg_fmt = _("Version %(req_ver)s is not supported by the API. Minimum "
                "is %(min_ver)s and maximum is %(max_ver)s.")


class InvalidSortKey(Invalid):
    msg_fmt = _("Sort key supplied was not valid.")


class InvalidStrTime(Invalid):
    msg_fmt = _("Invalid datetime string: %(reason)s")


class ServiceUnavailable(Invalid):
    msg_fmt = _("Service is unavailable at this time.")


class InvalidIpAddressError(Invalid):
    msg_fmt = _("%(address)s is not a valid IP v4/6 address.")


class InvalidVLANTag(Invalid):
    msg_fmt = _("VLAN tag is not appropriate for the port group "
                "%(bridge)s. Expected VLAN tag is %(tag)s, "
                "but the one associated with the port group is %(pgroup)s.")


class InvalidUUID(Invalid):
    msg_fmt = _("Expected a uuid but received %(uuid)s.")


class InvalidID(Invalid):
    msg_fmt = _("Invalid ID received %(id)s.")


class ConstraintNotMet(Error):
    msg_fmt = _("Constraint not met.")
    code = 412


class VersionNotFound(NotFound):
    message_format = _("Could not find version: %(version)s")


class InvalidIntValue(Invalid):
    msg_fmt = _("%(key)s must be an integer.")


class InvalidCidr(Invalid):
    msg_fmt = _("%(cidr)s is not a valid ip network.")


class InvalidAddress(Invalid):
    msg_fmt = _("%(address)s is not a valid ip address.")


class AddressOutOfRange(Invalid):
    msg_fmt = _("%(address)s is not within %(cidr)s.")


class DuplicateVlan(Error):
    msg_fmt = _("Detected existing vlan with id %(vlan)d")
    code = 409


class CidrConflict(Conflict):
    msg_fmt = _('Requested cidr (%(cidr)s) conflicts '
                'with existing cidr (%(other)s)')
    code = 409


class NoUniqueMatch(Conflict):
    msg_fmt = _("No Unique Match Found.")
    code = 409


class MalformedRequestBody(Error):
    msg_fmt = _("Malformed message body: %(reason)s")


class MarkerNotFound(NotFound):
    msg_fmt = _("Marker %(marker)s could not be found.")


# NOTE(johannes): NotFound should only be used when a 404 error is
# appropriate to be returned
class ConfigFileNotFound(NotFound):
    msg_fmt = _("Could not find config at %(path)s")


class PasteAppNotFound(NotFound):
    msg_fmt = _("Could not load paste app '%(name)s' from %(path)s")


class TaskAlreadyRunning(Error):
    msg_fmt = _("Task %(task_name)s is already running on host %(host)s")


class TaskNotRunning(Error):
    msg_fmt = _("Task %(task_name)s is not running on host %(host)s")


class UnexpectedError(Error):
    code = 500
    title = 'Internal Server Error'


class UnexpectedTaskStateError(Error):
    msg_fmt = _("Unexpected task state: expecting %(expected)s but "
                "the actual state is %(actual)s")


class UnexpectedDeletingTaskStateError(UnexpectedTaskStateError):
    pass


class FileNotFound(NotFound):
    msg_fmt = _("File %(file_path)s could not be found.")


class CryptoCAFileNotFound(FileNotFound):
    msg_fmt = _("The CA file for %(project)s could not be found")


class CryptoCRLFileNotFound(FileNotFound):
    msg_fmt = _("The CRL file for %(project)s could not be found")


class DBNotAllowed(Error):
    msg_fmt = _('%(binary)s attempted direct database access which is '
                'not allowed by policy')


class Base64Exception(Error):
    msg_fmt = _("Invalid Base 64 data for file %(path)s")


class UnsupportedObjectError(Error):
    msg_fmt = _('Unsupported object type %(objtype)s')


class OrphanedObjectError(Error):
    msg_fmt = _('Cannot call %(method)s on orphaned %(objtype)s object')


class IncompatibleObjectVersion(Error):
    msg_fmt = _('Version %(objver)s of %(objname)s is not supported')


class ReadOnlyFieldError(Error):
    msg_fmt = _('Cannot modify readonly field %(field)s')


class ObjectActionError(Error):
    msg_fmt = _('Object action %(action)s failed because: %(reason)s')


class ObjectFieldInvalid(Error):
    msg_fmt = _('Field %(field)s of %(objname)s is not an instance of Field')


class CoreAPIMissing(Error):
    msg_fmt = _("Core API extensions are missing: %(missing_apis)s")


class MissingParameter(Error):
    ec2_code = 'MissingParameter'
    msg_fmt = _("Not enough parameters: %(reason)s")
    code = 400


#########CloudVM#################################
class CloudVMExists(Error):
    errno = 21001
    msg_fmt = _("CloudVM with name %(name)s already exist.")
    
class CloudVMNotFound(NotFound):
    errno = 21002
    msg_fmt = _("CloudVM %(id)s could not be found.")
    
class CloudVMWithNameNotFound(NotFound):
    errno = 21003
    msg_fmt = _("CloudVM %(name)s could not be found.")

class CloudVMWithDeviceNotFound(NotFound):
    errno = 21004
    msg_fmt = _("CloudVM %(device_id)s could not be found.")
    
#########CloudOSVM#################################
class CloudOSVMExists(Error):
    errno = 21005
    msg_fmt = _("CloudOSVM with vm_id %(vm_id)s already exist.")

class CloudOSVMWithVMIDNotFound(NotFound):
    errno = 21006
    msg_fmt = _("CloudOSVM %(vm_id)s could not be found.")

class CloudOSVMNotFound(NotFound):
    errno = 21007
    msg_fmt = _("CloudOSVM %(id)s could not be found.")

class CloudOSVMWithVMIDExists(Error):
    errno = 21008
    msg_fmt = _("CloudOSVM with vm_id %(vm_id)s already exist.")

#########CloudVMImage#################################  
class CloudVMImageExists(Error):
    errno = 21009
    msg_fmt = _("CloudVMImage with name %(name)s already exist.")

class CloudVMImageNotFound(NotFound):
    errno = 21010
    msg_fmt = _("CloudVMImage %(id)s could not be found.")
    
class CloudVMImageWithVMNotFound(NotFound):
    errno = 21011
    msg_fmt = _("CloudVMImage with vm_id %(vm_id)s could not be found.")

#########CloudOSImage#################################  
class CloudOSImageExists(Error):
    errno = 21012
    msg_fmt = _("CloudOSImage with name %(name)s already exist.")

class CloudOSImageNotFound(NotFound):
    errno = 21013
    msg_fmt = _("CloudOSImage %(id)s could not be found.")


class CloudOSImageWithImageNotFound(NotFound):
    errno = 21014
    msg_fmt = _("CloudOSImage with image_id %(image_id)s could not be found.")


#########CloudVMSnapshot#################################
class CloudVMSnapshotExists(Error):
    errno = 21015
    msg_fmt = _("CloudVMShapshot with name %(name)s already exist.")


class CloudVMSnapshotNotFound(NotFound):
    errno = 21016
    msg_fmt = _("CloudVMSnapshot %(id)s could not be found.")


class CloudVMSnapshotWithVMNotFound(NotFound):
    errno = 21017
    msg_fmt = _("CloudVMSnapshot with vm_id %(vm_id)s could not be found.")

#########CloudOSSnapshot################################# 
class CloudOSSnapshotExists(Error):
    errno = 21018
    msg_fmt = _("CloudOSShapshot with name %(name)s already exist.")

class CloudOSSnapshotNotFound(NotFound):
    errno = 21019
    msg_fmt = _("CloudOSSnapshot %(id)s could not be found.")

class CloudOSSnapshotWithSnapNotFound(NotFound):
    errno = 21020
    msg_fmt = _("CloudOSSnapshot with snapshot_id %(snapshot_id)s could not be found.")


#########CloudVMVolume################################# 
class CloudVMVolExists(Error):
    errno = 21021
    msg_fmt = _("CloudVMVolume with name %(name)s already exist.")

class CloudVMVolNotFound(NotFound):
    errno = 21022
    msg_fmt = _("CloudVMVolume %(id)s could not be found.")


class CloudVMVolWithVMNotFound(NotFound):
    errno = 21023
    msg_fmt = _("CloudVMVolume with vm_id %(vm_id)s could not be found.")


class CloudVMVolWithVMAndVolNotFound(NotFound):
    errno = 21024
    msg_fmt = _("CloudVMVolume with %(vm_id)s and %(volume_id)s could not be found.")


#########CloudVolume################################# 
class CloudVolExists(Error):
    errno = 21024
    msg_fmt = _("CloudVolume with name %(name)s already exist.")


class CloudVolNotFound(NotFound):
    errno = 21025
    msg_fmt = _("CloudVolume %(id)s could not be found.")


#########CloudVolume################################# 
class CloudOSVolExists(Error):
    errno = 21026
    msg_fmt = _("CloudOSVolume with name %(name)s already exist.")

class CloudOSVolNotFound(NotFound):
    errno = 21027
    msg_fmt = _("CloudOSVolume %(id)s could not be found.")


class CloudOSVolWithVolIDNotFound(NotFound):
    errno = 21028
    msg_fmt = _("CloudOSVolume with volume_id %(id)s could not be found.")
    
#########CloudRouter#################################
class CloudRouterWithDeviceNotFound(NotFound):
    errno = 21029
    msg_fmt = _("CloudRouter with device_id %(device_id)s could not be found.")


############################################################
class VHostExist(Error):
    errno = 21030
    msg_fmt = _("VHost with name %(name)s already exist.")


class CloudDeviceNotFound(NotFound):
    errno = 21032
    msg_fmt = _("CloudDevice %(id)s could not be found.")


class ServiceNameExists(Conflict):
    msg_fmt = _("Service with name %(name)s exists.")


class ServiceTypeExists(Conflict):
    msg_fmt = _("Service with type %(type)s exists.")


class ServiceNotFound(NotFound):
    msg_fmt = _("Could not find service: %(service_id)s")


class ServiceNameNotFound(NotFound):
    msg_fmt = _("Could not find service with name: %(name)s")


class ServiceTypeNotFound(NotFound):
    msg_fmt = _("Could not find service with type: %(type)s")


class EndpointWithNameTypeNotFound(NotFound):
    msg_fmt = _("Could not find endpoint with name: %(name)s, type: %(type)s")


class EndpointWithNameTypeExists(Conflict):
    msg_fmt = _("Endpoint with name %(name)s, type %(type)s exists.")


class ConfigServiceTypeExists(Conflict):
    msg_fmt = _("Config with service type %(service_type)s exists.")


class ConfigNotFound(NotFound):
    msg_fmt = _("Could not find config: %(config_id)s")


class ConfigServiceTypeNotFound(NotFound):
    msg_fmt = _("Could not find config with service type: %(service_type)s")


class ConfigItemWithSectionItemExists(Conflict):
    msg_fmt = _("ConfigItem with section: %(section)s, item: %(item)s exists.")


class ConfigItemNotFound(NotFound):
    msg_fmt = _("Could not find config item: %(item_id)s")


class ConfigItemWithSectionItemNotFound(NotFound):
    msg_fmt = _("Could not find config item with section: "
                "%(section)s, name: %(name)s")


class RoleNameExists(Conflict):
    msg_fmt = _("Role with name %(name)s exists.")


class RolePermissionExists(Conflict):
    msg_fmt = _("Role(%(role_id)s) with permission %(permission_id)s exists.")


class RoleUserExists(Conflict):
    msg_fmt = _("Role(%(role_id)s) with user %(user_id)s exists.")


class RoleNotFound(NotFound):
    msg_fmt = _("Could not find role: %(role_id)s")


class RoleNameNotFound(NotFound):
    msg_fmt = _("Could not find role with name: %(name)s")


class RolePermissionNotFound(NotFound):
    msg_fmt = _("Could not find permission %(permission_id)s "
                "in role %(role_id)s")


class RoleUserNotFound(NotFound):
    msg_fmt = _("Could not find user %(user_id)s "
                "with role %(role_id)s")

class ResourceNotFound(NotFound):
    msg_fmt = _("Could not find resource %(resource)s ")


class ModuleWithArgsExist(Conflict):
    msg_fmt = _("Module with with service_id: %(service_id)s, "
                "module: %(module)s exists.")


class ModuleNotFound(NotFound):
    msg_fmt = _("Could not find module: %(module_id)s")


class ModuleWithArgsNotFound(NotFound):
    msg_fmt = _("Could not find module with service_id: %(service_id)s, "
                "module: %(module)s")


class PermissionWithArgsExist(Conflict):
    msg_fmt = _("Permission with with module_id: %(module_id)s, "
                "permission: %(permission)s exists.")


class PermissionNotFound(NotFound):
    msg_fmt = _("Could not find permission: %(permission_id)s")


class PermissionWithArgsNotFound(NotFound):
    msg_fmt = _("Could not find permission with module_id: %(module_id)s, "
                "permission: %(permission)s")


class ResourceWithArgsExist(Conflict):
    msg_fmt = _("Resource with with service_id: %(service_id)s, "
                "resource: %(resource)s exists.")


class ResourceNotFound(NotFound):
    msg_fmt = _("Could not find resource: %(resource_id)s")


class ResourceWithArgsNotFound(NotFound):
    msg_fmt = _("Could not find resource with service_id: %(service_id)s, "
                "resource: %(resource)s")


class ResourceConfigWithArgsExist(Conflict):
    msg_fmt = _("ResourceConfig with with resource_id: %(resource_id)s, "
                "type: %(type)s exists.")


class ResourceConfigNotFound(NotFound):
    msg_fmt = _("Could not find resource_config: %(resource_config_id)s")


class ResourceConfigWithArgsNotFound(NotFound):
    msg_fmt = _("Could not find resource_config with "
                "resource_id: %(resource_id)s, "
                "type: %(type)s")


class UserQuotaWithArgsExist(Conflict):
    msg_fmt = _("UserQuota with with user_id: %(user_id)s, "
                "resource_id: %(resource_id)s exists.")


class UserQuotaNotFound(NotFound):
    msg_fmt = _("Could not find user_quota_id: %(user_quota_id)s")


class UserQuotaWithArgsNotFound(NotFound):
    msg_fmt = _("Could not find user quota with user_id: %(user_id)s, "
                "resource_id: %(resource_id)s")


class SecurityError(Error):
    """Avoids exposing details of security failures, unless in debug mode."""
    amendment = _('(Disable debug mode to suppress these details.)')

    def _build_message(self, message, **kwargs):
        """Only returns detailed messages in debug mode."""
        if 0:  # TODO(hexiaoxi): read from CONF.debug:
            return _('%(message)s %(amendment)s') % {
                'message': message or self.message_format % kwargs,
                'amendment': self.amendment}
        else:
            return self.message_format % kwargs


class Unauthorized(Error):
    errno = 21031
    msg_fmt = _("The request you have made requires authentication.")
    code = 401
    title = 'Unauthorized'


class ExperimentNotFound(NotFound):
    errno = 20001
    msg_fmt = _("Could not find experiment: %(expt_id)s")


class ExptApplicationNotFound(NotFound):
    errno = 20002
    msg_fmt = _("Experiment application could not be found.")
    

class VHostNotFound(NotFound):
    errno = 20003
    msg_fmt = _("Could not find vhost: %(vhost_id)s")


class VrouterNotFoundByDevice(NotFound):
    errno = 20004
    msg_fmt = _("Could not find vrouter by device: %(device_id)s")

    
class TopoHasNoSubnet(NotFound):
    errno = 20005
    msg_fmt = _("Could not find subnet in topo: %(topo_id)s")


class PortFloatingipExist(Conflict):
    errno = 20006
    msg_fmt = _("Port floatingip exist: %(port_id)s")


class InterfaceNotFound(NotFound):
    errno = 20007
    msg_fmt = _("Could not find router interface: %(interface_id)s")


class VMNotFound(NotFound):
    errno = 20008
    msg_fmt = _("Could not find vm: %(vm_id)s")


class NEExist(Conflict):
    errno = 20009
    msg_fmt = _("Network element with name %(ne_name)s exist.")
    

class NEStatExist(Conflict):
    errno = 20010
    msg_fmt = _("Network element stat with id %(ne_id)s exist.")


class NEIconExist(Conflict):
    errno = 20011
    msg_fmt = _("Network element icon with id %(ne_id)s exist.")
    
    
class NEPortExist(Conflict):
    errno = 20012
    msg_fmt = _("Network element port with id %(ne_id)s, no %(port_no)s exist.")
    
class NENotFound(NotFound):
    errno = 20013
    msg_fmt = _("Network element %(ne)s could not be found.")


class ExptLimitExceeded(ResourceNotEnough):
#     code = 1001
    errno = 20014
    msg_fmt = _("Maximum number of experiment exceeded.")

class VmLimitExceeded(ResourceNotEnough):
#     code = 1002
    errno = 20015
    msg_fmt = _("Maximum number of vm exceeded.")


class MemoryLimitExceeded(ResourceNotEnough):
#     code = 1003
    errno = 20016
    msg_fmt = _("Maximum number of memory exceeded.")


class CpuLimitExceeded(ResourceNotEnough):
#     code = 1004
    errno = 20017
    msg_fmt = _("Maximum number of cpu exceeded.")


class DiskLimitExceeded(ResourceNotEnough):
#     code = 1005
    errno = 20018
    msg_fmt = _("Maximum number of disk exceeded.")


class VSwitchPortLimitExceeded(Error):
    # code = 1006
    errno = 20019
    msg_fmt = _("Maximum number of vswitch port exceeded.")


class VSwitchNotFound(NotFound):
    errno = 20020
    msg_fmt = _("Could not find vswitch: %(vswitch_id)s")


class CloudDBException(Error):
    code = 3001
    msg_fmt = _("DB operate failed.")


class CloudException(Error):
    code = 3002
    msg_fmt = _("Cloud experiment exception.")


class NETagExist(Error):
    code = 4001
    msg_fmt = _("Network element tag with name %(tag_name)s exist.")


class VMFlavorNameExist(NotFound):
    errno = 20020
    msg_fmt = _("VMFlavor with name \'%(name)s\' exist.")


class VMFlavorWithCloudNotFound(NotFound):
    errno = 20021
    msg_fmt = _("VM Flavor with cloud %(id)s could not be found.")


class VMFlavorExist(NotFound):
    errno = 20022
    msg_fmt = _("VM Flavor  could not be found.")


class VMFlavorNotFound(NotFound):
    errno = 20070
    msg_fmt = _("Could not find flavor: %(id)s")


class CreateExperimentFailed(Error):
    errno = 20023
    msg_fmt = _("Experiment created failed.")

    def __init__(self, message=None, **kwargs):
        super(CreateExperimentFailed, self).__init__(message=message, **kwargs)
        if 'expt_id' in self.kwargs:
            self.business_info = dict(expt_id=self.kwargs['expt_id'])


class CanNotSnapshotExpt(Error):
    errno = 20071
    msg_fmt = _("Experiment %(expt_id)s can not create snapshot with current state.")


class ExptSnapshotNotFound(NotFound):
    errno = 20072
    msg_fmt = _("Could not find experiment snapshot: %(id)s")


class VolumeNotFound(NotFound):
    errno = 20073
    msg_fmt = _("Could not find volume: %(id)s")


class VolumeSnapshotNotFound(NotFound):
    errno = 20074
    msg_fmt = _("Could not find volume snapshot: %(id)s")


class CanNotDelExptSnapshot(Error):
    errno = 20075
    msg_fmt = _("Experiment snapshot %(snapshot_id)s can not be deleted with current state.")


class CanNotRestoreExptSnapshot(Error):
    errno = 20076
    msg_fmt = _("Experiment snapshot %(snapshot_id)s can not be restored with current state.")


class ExperimentExist(Conflict):
#     code = 410
    errno = 20024
    msg_fmt = _("Experiment with name %(name)s exist.")
    title = 'Experiment has exist'


class ExperimentConfigExist(Conflict):
    errno = 20025
    msg_fmt = _("Experiment config exist.")
    title = 'Experiment config exist'


class TopoExistInExpt(Conflict):
    errno = 20026
    msg_fmt = _("Topo %(topo_id)s has exist in experiment %(expt_id)s.")


class DeviceCreatedFailed(Error):
    errno = 20027
    msg_fmt = _("Device created failed.")


class CanNotCreateDeviceInMininet(Error):
    errno = 20028
    msg_fmt = _("Can not create device with type %(type)s in mininet experiment.")
    

class DeleteExperimentFailed(Error):
    errno = 20045
    msg_fmt = _("Delete experiment %(expt_id)s failed.")

class ExptCreateSuspendByDelete(Error):
    msg_fmt = _("Experiment with name %(name)s suspended by deleting.")


############################# device #########################################
class CanNotReStartDevice(Error):
    errno = 20029
    msg_fmt = _("Device %(device_id)s could not be restart with state %(state)s.")


class CanNotStartDevice(Error):
    errno = 20030
    msg_fmt = _("Device %(device_id)s could not be start with state %(state)s.")


class CanNotStopDevice(Error):
    errno = 20031
    msg_fmt = _("Device %(device_id)s could not be stop with state %(state)s.")


class CannotFoundConfig(Error):
    errno = 20032
    msg_fmt = _("Could not find config!")


class TopologyNotFound(NotFound):
    errno = 20033
    msg_fmt = _("Could not find topology: %(topo_id)s")


class NetworkNotFound(NotFound):
    errno = 20034
    msg_fmt = _("Could not find network: %(net_id)s")


class SubnetNotFound(NotFound):
    errno = 20035
    msg_fmt = _("Could not find subnet: %(subnet_id)s")


class PortNotFound(NotFound):
    errno = 20036
    msg_fmt = _("Could not find port: %(port_id)s")


class DeviceNotFound(NotFound):
    errno = 20037
    msg_fmt = _("Could not find device: %(device_id)s")


class RouterNotFound(NotFound):
    errno = 20038
    msg_fmt = _("Could not find router: %(router_id)s")


class FloatingipNotFound(NotFound):
    errno = 20039
    msg_fmt = _("Could not find floatingip: %(floatingip_id)s")


class OSPortNotFound(NotFound):
    errno = 20040
    msg_fmt = _("Could not find os port of port: %(port_id)s")


class OSRouterNotFound(NotFound):
    errno = 20041
    msg_fmt = _("Could not find os router of router: %(router_id)s")


class NetworkLimitExceeded(ResourceNotEnough):
    # code = 1007
    errno = 20042
    msg_fmt = _("Maximum number of network exceeded.")


class SubnetLimitExceeded(ResourceNotEnough):
    # code = 1008
    errno = 20043
    msg_fmt = _("Maximum number of subnet exceeded.")


class RouterLimitExceeded(ResourceNotEnough):
    # code = 1009
    errno = 20044
    msg_fmt = _("Maximum number of router exceeded.")


class ExperimentConfigTagExist(Conflict):
    errno = 20045
    msg_fmt = _("Experiment config tag exist.")
    title = 'Experiment config tag exist'


class ExptPlatformNotFound(NotFound):
    errno = 20046
    msg_fmt = _("Could not find experiment platform: %(err_msg)s")


class ExptPlatformExist(Conflict):
    errno = 20047
    msg_fmt = _("Experiment platform with name %(name)s exist.")
    title = 'Experiment platform has exist'


class CreateExptPlatformFailed(Error):
    errno = 20048
    msg_fmt = _("Experiment platform with name %(name)s created failed")


class PortPairNotFound(NotFound):
    errno = 20049
    msg_fmt = _("Could not find port pair: %(port_pair_id)s")


class FlowClassifierNotFound(NotFound):
    errno = 20053
    msg_fmt = _("Could not find flow classifier: %(flow_classifier_id)s")


class PortPairGroupNotFound(NotFound):
    errno = 20051
    msg_fmt = _("Could not find port pair group: %(port_pair_group_id)s")


class PortChainNotFound(NotFound):
    errno = 20052
    msg_fmt = _("Could not find port pair: %(port_Chain_id)s")


class ManageNetworkNotFound(NotFound):
    errno = 20054
    msg_fmt = _("Could not find manage network: %(net_id)s")


class L2NetworkNotFound(NotFound):
    errno = 20055
    msg_fmt = _("Could not find l2 network: %(net_id)s")


class DHCPNetworkNotFound(NotFound):
    errno = 20056
    msg_fmt = _("Could not find dhcp network: %(net_id)s")


class CTNetworkNotFound(NotFound):
    errno = 20057
    msg_fmt = _("Could not find controller network: %(net_id)s")


class PoolFloatingIPNotFound(NotFound):
    errno = 20058
    msg_fmt = _("Could not find pool floatingip: %(floatingip_id)s")


class CanNotStartExpt(Error):
    errno = 20059
    msg_fmt = _("Experiment %(expt_id)s could not be start with current state.")


class CanNotStopExpt(Error):
    errno = 20060
    msg_fmt = _("Experiment %(expt_id)s could not be stop with current state.")


class CanNotUpdateExpt(Conflict):
    errno = 20061
    msg_fmt = _("Experiment %(expt_id)s could not be updated with current state.")

class CanNotAddController(Conflict):
    errno = 20062
    msg_fmt = _("Experiment %(expt_id)s can not add controller.")

class CanNotAddSubnet(Conflict):
    errno = 20063
    msg_fmt = _("Experiment %(expt_id)s can not add subnet.")

class CanNotAddLink(Conflict):
    errno = 20064
    msg_fmt = _("Experiment %(expt_id)s can not add link.")

class CanNotDelDevice(Conflict):
    errno = 20065
    msg_fmt = _("Experiment %(expt_id)s can not del device.")

class CanNotDelSubnet(Conflict):
    errno = 20066
    msg_fmt = _("Experiment %(expt_id)s can not del subnet.")

class CanNotDelLink(Conflict):
    errno = 20067
    msg_fmt = _("Experiment %(expt_id)s can not del link.")

class CanNotEditDevice(Conflict):
    errno = 20068
    msg_fmt = _("Experiment %(expt_id)s can not edit device.")

class CanNotEditSubnet(Conflict):
    errno = 20069
    msg_fmt = _("Experiment %(expt_id)s can not edit subnet.")

class ConnectionOSError(Error):
    errno = 26001
    msg_fmt = _("Failed to establish a new connection to openstack.")

class DeleteDeviceFailed(Error):
    errno = 26002
    msg_fmt = _("Delete device %(device_id)s failed.")

class DeleteSubnetFailed(Error):
    errno = 26003
    msg_fmt = _("Delete subnet %(subnet_id)s failed.")

class DeleteVlinkFailed(Error):
    errno = 26004
    msg_fmt = _("Delete vlink %(vlink_id)s failed.")

class UpdateSubnetFailed(Error):
    errno = 26005
    msg_fmt = _("Update subnet %(subnet_id)s failed.")

class UpdateVlinkFailed(Error):
    errno = 26006
    msg_fmt = _("Update vlink %(vlink_id)s failed.")

class CreateNeworkFailed(Error):
    errno = 26007
    msg_fmt = _("Create network failed.")

class CreateDeviceFailed(Error):
    errno = 26008
    msg_fmt = _("Create device failed.")


############################# course start ########################################

class CourseInUsing(Conflict):
    errno = 30001
    msg_fmt = _("Course is using.")
    title = 'Course is using'

class CourseNameExist(Conflict):
    errno = 30002
    msg_fmt = _("Course name exist.")
    title = 'Course name exist'

class CategoryNameExist(Conflict):
    errno = 30003
    msg_fmt = _("Course category name exist.")
    title = 'Course category name exist'

class CourseNotFound(NotFound):
    errno = 30005
    msg_fmt = _("Course not found.")
    title = 'Course not found'

class CategoryNotFound(NotFound):
    errno = 30006
    msg_fmt = _("Course category not found.")
    title = 'Course category not found'

class TemplateNotFound(NotFound):
    errno = 30007
    msg_fmt = _("Template not found.")
    title = 'Template not found'
############################# course end #########################################

############################# mano start ########################################

class VnfdNotFound(NotFound):
    errno = 40001
    msg_fmt = _("Could not find vnfd: %(vnfd_id)s")

class VnfNotFound(NotFound):
    errno = 40002
    msg_fmt = _("Could not find vnf: %(vnf_id)s")

class VnffgdNotFound(NotFound):
    errno = 40003
    msg_fmt = _("Could not find vnffgd: %(vnffgd_id)s")

class VnffgNotFound(NotFound):
    errno = 40004
    msg_fmt = _("Could not find vnffg: %(vnffg_id)s")

class VimNotFound(NotFound):
    errno = 40005
    msg_fmt = _("Could not find vim: %(vim_id)s")
############################# mano end #########################################

############################# nfv_experiment start ########################################

class NfvNsNotFound(NotFound):
    errno = 50001
    msg_fmt = _("Could not find nfvns: %(nfvns_id)s")

class NfvVmNotFound(NotFound):
    errno = 50002
    msg_fmt = _("Could not find nfvvm: %(nfvvm_id)s")

class NfvRouterNotFound(NotFound):
    errno = 50003
    msg_fmt = _("Could not find nfvrouter: %(nfvrouter_id)s")

class NfvSubnetNotFound(NotFound):
    errno = 50004
    msg_fmt = _("Could not find nfvsubnet: %(nfvsubnet_id)s")

class NfvVnffgNotFound(NotFound):
    errno = 50005
    msg_fmt = _("Could not find nfvvnffg: %(nfvvnffg_id)s")

############################# nfv_experiment end #########################################

class EvaluationNotFound(NotFound):
    errno = 50006
    msg_fmt = _("evaluation %(id)s could not be found.")

class QuestionNotFound(NotFound):
    errno = 50007
    msg_fmt = _("question %(id)s could not be found.")

class NoteNotFound(NotFound):
    errno = 50008
    msg_fmt = _("note %(id)s could not be found.")

class DiyExptApplyNotFound(NotFound):
    errno = 50009
    msg_fmt = _("diy expt apply %(id)s could not be found.")

class DiyExptWhiteListExist(Conflict):
    errno = 50010
    msg_fmt = _("diy expt white list exist.")

class CommentNotFound(NotFound):
    errno = 50011
    msg_fmt = _("comment %(id)s could not be found.")

class ArticleNotFound(NotFound):
    errno = 50012
    msg_fmt = _("article %(id)s could not be found.")

class UserCellPhoneExists(Conflict):
    errno = 31
    msg_fmt = _("User with cellphone %(cellphone)s exists.")


class UserNameExistsWithUniversity(Conflict):
    errno = 31
    msg_fmt = _("User name %(name)s with university id %(site_id)s exists.")

class UserNameExists(Conflict):
    errno = 1
    msg_fmt = _("User with name %(name)s exists.")


class UserNotFound(NotFound):
    errno = 4
    msg_fmt = _("Could not find user: %(user_id)s")
