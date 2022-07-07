import logging
import traceback

from keystoneauth1 import adapter
from keystoneauth1 import session
from keystoneauth1.exceptions import catalog
from keystoneauth1.exceptions import http
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
import requests
import six
import urllib.parse as urlparse


import urllib3
urllib3.disable_warnings()

from coriolismetalhub import exceptions


LOG = logging.getLogger(__name__)


_DEFAULT_SERVICE_TYPE = 'metal-hub'
_DEFAULT_SERVICE_INTERFACE = 'public'
_DEFAULT_API_VERSION = 'v1'

_DEFAULT_IDENTITY_API_VERSION = '3'
_IDENTITY_API_VERSION_2 = ['2', '2.0']
_IDENTITY_API_VERSION_3 = ['3']


class _HTTPSClientBase(object):

    def __init__(self, endpoint, cert, key, ca):
        self._cert = cert
        self._key = key
        self._ca = ca
        self._cli_obj = None
        self._endpoint = endpoint

    @property
    def _cli(self):
        if self._cli_obj is not None:
            return self._cli_obj

        cert = (self._cert, self._key)
        sess = requests.Session()
        sess.cert = cert
        sess.verify = self._ca
        return sess


class KeystoneClient(adapter.Adapter):
    def __init__(self, session, project_id=None, **kwargs):
        kwargs.setdefault('interface', _DEFAULT_SERVICE_INTERFACE)
        kwargs.setdefault('service_type', _DEFAULT_SERVICE_TYPE)
        kwargs.setdefault('version', _DEFAULT_API_VERSION)
        endpoint = kwargs.pop('endpoint', None)

        super(KeystoneClient, self).__init__(session, **kwargs)

        if endpoint:
            self.endpoint_override = '{0}/{1}'.format(endpoint, self.version)


class AgentClient(_HTTPSClientBase):

    def list_disks(self, include_virtual=False):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/disks/")
        ret = self._cli.get(url, params={"includeVirtual": include_virtual})
        ret.raise_for_status()
        return ret.json()

    def get_disk(self, disk_id):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/disks/%s/" % disk_id)
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def list_snapstore_locations(self):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapstorelocations/")
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def list_snapstore_mappings(self):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapstoremappings/")
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def create_snapstore_mapping(self, snapstore_id, disk_id):
        data =  {
            "snapstore_location_id": snapstore_id,
            "tracked_disk_id": disk_id,
        }
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapstoremappings/")
        ret = self._cli.post(url, json=data)
        ret.raise_for_status()
        return ret.json()

    def create_snapshot(self, disks=None):
        if disks is None:
            srv_disks = self.list_disks()
            disks = []
            for disk in srv_disks:
                disks.append(disk["id"])

        if len(disks) == 0:
            raise ValueError("no disks found for server")

        data = {
            "tracked_disk_ids": disks,
        }

        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapshots/")
        ret = self._cli.post(url, json=data)
        ret.raise_for_status()
        return ret.json()

    def list_snapshots(self):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapshots/")
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def get_snapshot(self, snapshot_id):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapshots/%s/" % snapshot_id)
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def delete_snapshot(self, snapshot_id):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/snapshots/%s" % snapshot_id)
        ret = self._cli.delete(url)
        ret.raise_for_status()
        return

    def get_snapshot_changes(self, snapshot_id, disk_id,
                             generation_id=None, previous_number=None):
        params = {
            "previousGenerationID": generation_id,
            "previousNumber": previous_number,
        }
        url = urlparse.urljoin(
            self._endpoint,
            "/api/v1/snapshots/%s/changes/%s/" % (snapshot_id, disk_id))
        ret = self._cli.get(url, params=params)
        ret.raise_for_status()
        return ret.json()

    def download_chunk(self, snapshot_id, disk_id, offset,
                       length, stream=False):
        url = urlparse.urljoin(
            self._endpoint,
            "/api/v1/snapshots/%s/consume/%s/" % (snapshot_id, disk_id))
        start = offset
        end = offset + length - 1
        headers = {
            "Range": "bytes=%s-%s" % (start, end)
        }
        ret = self._cli.get(
            url, headers=headers, stream=stream)
        ret.raise_for_status()

        if stream:
            return ret
        return ret.content

    def systeminfo(self):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/systeminfo/")
        ret = self._cli.delete(url)
        ret.raise_for_status()
        return ret.json()


class HubClient(object):
    def __init__(
            self, endpoint, client_certs, ks_session=None):
        self._endpoint = endpoint
        if ks_session:
            self._ks_cli = KeystoneClient(session=ks_session)

        self._cert = client_certs['cert']
        self._key = client_certs['key']
        self._ca = client_certs['ca']

    @property
    def _token(self):
        return self._ks_cli.get_token()

    @property
    def _auth_headers(self):
        head = {
            "X-Auth-Token": self._token,
        }
        return head

    def list_servers(self, hostname_like=None):
        headers = self._auth_headers
        params = None
        if hostname_like is not None:
            params = {"hostname": hostname_like}
        url = urlparse.urljoin(self._endpoint, "/api/v1/servers")
        ret = requests.get(url, params=params, headers=headers)
        ret.raise_for_status()
        return ret.json()

    def get_server(self, serverID):
        headers = self._auth_headers
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/%s" % serverID)
        ret = requests.get(url, headers=headers)
        ret.raise_for_status()
        return ret.json()

    def add_server(self, endpoint, cert=None, key=None, ca=None):
        headers = self._auth_headers
        data = {
            "api_endpoint": endpoint,
            "ca_cert": ca,
            "tls_cert": cert,
            "tls_key": key,
        }
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/")
        ret = requests.post(url, json=data, headers=headers)
        ret.raise_for_status()
        return ret.json()

    def update_server(self, serverID, endpoint, cert=None, key=None, ca=None):
        headers = self._auth_headers
        data = {
            "api_endpoint": endpoint,
            "ca_cert": ca,
            "tls_cert": cert,
            "tls_key": key,
        }
        url = urlparse.urljoin(self._endpoint, "/api/v1/servers/%s" % serverID)
        ret = requests.put(url, json=data, headers=headers)
        ret.raise_for_status()
        return ret.json()

    def refresh_server(self, serverID):
        headers = self._auth_headers
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/%s/refresh" % serverID)
        ret = requests.get(url, headers=headers)
        ret.raise_for_status()
        return ret.json()

    def remove_server(self, serverID):
        headers = self._auth_headers
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/%s" % serverID)
        ret = requests.delete(url, headers=headers)
        ret.raise_for_status()
        return

    def get_client_for_server(self, serverID):
        srv = self.get_server(serverID)
        cli = AgentClient(
            endpoint=srv["api_endpoint"],
            cert=self._cert,
            key=self._key,
            ca=self._ca)
        return cli

def _get_tls_auth_kwargs_from_options(options):
    if None in (options.endpoint,
                options.client_cert,
                options.client_key,
                options.ca_cert):
        raise Exception(
            "Missing auth data. Please specify --endpoint, "
            "--ca-cert, --client-cert, --client-key")
    kw = {
        "cert": options.client_cert,
        "key": options.client_key,
        "ca": options.ca_cert,
    }
    return kw


def check_auth_arguments(args, api_version=None, raise_exc=False):
    """Verifies that we have the correct arguments for authentication

    Supported Keystone v3 combinations:
        - Project Id
        - Project Name + Project Domain Name
        - Project Name + Project Domain Id
    Supported Keystone v2 combinations:
        - Tenant Id
        - Tenant Name
    """
    successful = True
    v3_arg_combinations = [
        args.os_project_id,
        args.os_project_name and args.os_project_domain_name,
        args.os_project_name and args.os_project_domain_id
    ]
    v2_arg_combinations = [args.os_tenant_id, args.os_tenant_name]

    # Keystone V3
    if not api_version or api_version == _DEFAULT_IDENTITY_API_VERSION:
        if not any(v3_arg_combinations):
            msg = ('ERROR: please specify the following --os-project-id or'
                    ' (--os-project-name and --os-project-domain-name) or '
                    ' (--os-project-name and --os-project-domain-id)')
            successful = False
    # Keystone V2
    else:
        if not any(v2_arg_combinations):
            msg = ('ERROR: please specify --os-tenant-id or'
                    ' --os-tenant-name')
            successful = False

    if not successful and raise_exc:
        raise Exception(msg)

    return successful



def build_kwargs_based_on_version(args, api_version=None):
    if not api_version or api_version == _DEFAULT_IDENTITY_API_VERSION:
        kwargs = {
            'project_id': args.os_project_id,
            'project_name': args.os_project_name,
            'user_domain_id': args.os_user_domain_id,
            'user_domain_name': args.os_user_domain_name,
            'project_domain_id': args.os_project_domain_id,
            'project_domain_name': args.os_project_domain_name
        }
    else:
        kwargs = {
            'tenant_name': args.os_tenant_name,
            'tenant_id': args.os_tenant_id
        }

    # Return a dictionary with only the populated (not None) values
    return dict((k, v) for (k, v) in six.iteritems(kwargs) if v)


def create_keystone_session(args, api_version, kwargs_dict, auth_type):
    # Make sure we have the correct arguments to function
    check_auth_arguments(args, api_version, raise_exc=True)

    kwargs = build_kwargs_based_on_version(args, api_version)
    kwargs.update(kwargs_dict)

    if api_version in _IDENTITY_API_VERSION_2:
        method = v2.Token if auth_type == 'token' else v2.Password
    else:
        if not api_version or api_version not in _IDENTITY_API_VERSION_3:
            LOG.warn(
                "The identity version <{0}> is not in supported "
                "versions <{1}>, falling back to <{2}>.".format(
                    api_version,
                    _IDENTITY_API_VERSION_2 + _IDENTITY_API_VERSION_3,
                    _DEFAULT_IDENTITY_API_VERSION
                )
            )
        method = v3.Token if auth_type == 'token' else v3.Password

    auth = method(**kwargs)

    return session.Session(auth=auth)


def get_client_from_options(options):
    client_certs =  _get_tls_auth_kwargs_from_options(options)
    created_client = None

    api_version = options.os_identity_api_version
    if options.no_auth and options.os_auth_url:
        raise Exception(
            'ERROR: argument --os-auth-url/-A: not allowed '
            'with argument --no-auth/-N'
        )

    if options.no_auth:
        if not all([options.endpoint, options.os_tenant_id or
                    options.os_project_id]):
            raise Exception(
                'ERROR: please specify --endpoint and '
                '--os-project-id (or --os-tenant-id)')
        created_client = HubClient(options.endpoint, client_certs)
    # Token-based authentication
    elif options.os_auth_token:
        if not options.os_auth_url:
            raise Exception('ERROR: please specify --os-auth-url')
        token_kwargs = {
            'auth_url': options.os_auth_url,
            'token': options.os_auth_token
        }
        session = create_keystone_session(
            options, api_version, token_kwargs, auth_type='token'
        )
        created_client = HubClient(
            options.endpoint, client_certs, ks_session=session)

    # Password-based authentication
    elif options.os_auth_url:
        password_kwargs = {
            'auth_url': options.os_auth_url,
            'password': options.os_password,
            'user_id': options.os_user_id,
            'username': options.os_username,
        }
        session = create_keystone_session(
            options, api_version, password_kwargs, auth_type='password'
        )
        created_client = HubClient(
            options.endpoint, client_certs, ks_session=session)
    else:
        raise Exception('ERROR: please specify authentication credentials')

    return created_client
