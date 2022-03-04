import requests
import urllib.parse as urlparse


import urllib3
urllib3.disable_warnings()


class _ClientBase(object):

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


class AgentClient(_ClientBase):

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


class HubClient(_ClientBase):
    def list_servers(self, hostname_like=None):
        params = None
        if hostname_like is not None:
            params = {"hostname": hostname_like}
        url = urlparse.urljoin(self._endpoint, "/api/v1/servers")
        ret = self._cli.get(url, params=params)
        ret.raise_for_status()
        return ret.json()

    def get_server(self, serverID):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/%s" % serverID)
        ret = self._cli.get(url)
        ret.raise_for_status()
        return ret.json()

    def add_server(self, endpoint, cert=None, key=None, ca=None):
        data = {
            "api_endpoint": endpoint,
            "ca_cert": ca,
            "tls_cert": cert,
            "tls_key": key,
        }
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/")
        ret = self._cli.post(url, json=data)
        ret.raise_for_status()
        return ret.json()

    def remove_server(self, serverID):
        url = urlparse.urljoin(
            self._endpoint, "/api/v1/servers/%s" % serverID)
        ret = self._cli.delete(url)
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

def _get_auth_kwargs_from_options(options):
    if None in (options.endpoint,
                options.client_cert,
                options.client_key,
                options.ca_cert):
        raise Exception(
            "Missing auth data. Please specify --endpoint, "
            "--ca-cert, --client-cert, --client-key")
    kw = {
        "endpoint": options.endpoint,
        "cert": options.client_cert,
        "key": options.client_key,
        "ca": options.ca_cert,
    }
    return kw


def get_client_from_options(options):
    kw =  _get_auth_kwargs_from_options(options)
    return HubClient(**kw)
