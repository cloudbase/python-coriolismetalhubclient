import json

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

from coriolismetalhub import client


class Servers(Lister):

    def get_parser(self, prog_name):
        parser = super(Servers, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        servers = cli.list_servers()
        ret = [
            ["ID", "Hostname", "API Endpoint", "Alive"]
        ]

        items = []
        for server in servers:
            item = [
                server["id"],
                server.get("hostname"),
                server["api_endpoint"],
                server.get("active"),
            ]
            items.append(item)

        ret.append(items)
        return ret


class ShowServer(ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        server = cli.get_server(args.id)
        disks = server.get('disks', {})
        nics = server.get('nics', {})

        columns = ('ID',
                   'Hostname',
                   "API Endpoint",
                   "Physical Cores",
                   "Memory",
                   "Firmware type",
                   "Alive",
                   "Disks",
                   "NICs")
        data = (server["id"],
                server.get("hostname"),
                server["api_endpoint"],
                server.get("physical_cores"),
                server.get("memory"),
                server.get("firmware_type"),
                server.get("active"),
                json.dumps(disks, indent=2),
                json.dumps(nics, indent=2))
        return (columns, data)


class CreateServer(ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)
        parser.add_argument("endpoint", help="The endpoint of the server.")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        server = cli.add_server(args.endpoint)
        columns = ('ID',
                   'Hostname',
                   "API Endpoint",
                   "Physical Cores",
                   "Memory",
                   "Firmware type",
                   "Alive")
        data = (server["id"],
                server.get("hostname"),
                server["api_endpoint"],
                server.get("physical_cores"),
                server.get("memory"),
                server.get("firmware_type"),
                server.get("active"))
        return (columns, data)


class RemoveServer(Command):

    def get_parser(self, prog_name):
        parser = super(RemoveServer, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(self._cmd_options)
        cli.remove_server(args.id)
