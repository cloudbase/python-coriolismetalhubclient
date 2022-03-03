import json

from cliff.lister import Lister
from cliff.show import ShowOne
from cliff.command import Command

from coriolismetalhub import client


class ListSnapshots(Lister):

    def get_parser(self, prog_name):
        parser = super(ListSnapshots, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        srv_cli = cli.get_client_for_server(args.id)
        snapshots = srv_cli.list_snapshots()
        ret = [
            ["Snapshot ID", "Server ID", "Disks"]
        ]
        items = []
        for snap in snapshots:
            disks = []
            for i in snap["volume_snapshots"]:
                disks.append(i["original_device"]["device_path"])
            item = [
                snap["snapshot_id"],
                args.id,
                ", ".join(disks),
            ]
            items.append(item)

        ret.append(items)
        return ret


class CreateSnapshot(ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateSnapshot, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        srv_cli = cli.get_client_for_server(args.id)
        snap = srv_cli.create_snapshot()
        columns = (
            "Snapshot ID", "Server ID",
            "Disks",
        )
        disks = []
        for i in snap["volume_snapshots"]:
            snap_info = {
                "snapshot_number": i["snapshot_number"],
                "generation_id": i["generation_id"],
                "tracking_id": i["original_device"]["tracking_id"],
                "device_path": i["original_device"]["device_path"],
                "snapshot_image": i["snapshot_image"]["device_path"],
            }
            disks.append(json.dumps(snap_info, indent=2))

        data = (
            snap["snapshot_id"],
            args.id,
            "\n\n".join(disks),
        )
        return (columns, data)


class ShowSnapshot(ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowSnapshot, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        parser.add_argument("snapshotID", help="The ID of the snapshot")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        srv_cli = cli.get_client_for_server(args.id)
        snap = srv_cli.get_snapshot(args.snapshotID)
        columns = (
            "Snapshot ID", "Server ID",
            "Disks",
        )

        disks = []
        for i in snap["volume_snapshots"]:
            snap_info = {
                "snapshot_number": i["snapshot_number"],
                "generation_id": i["generation_id"],
                "tracking_id": i["original_device"]["tracking_id"],
                "device_path": i["original_device"]["device_path"],
                "snapshot_image": i["snapshot_image"]["device_path"],
            }
            disks.append(json.dumps(snap_info, indent=2))
        data = (
            snap["snapshot_id"],
            args.id,
            "\n\n".join(disks)
        )
        return (columns, data)


class DeleteSnapshot(Command):

    def get_parser(self, prog_name):
        parser = super(DeleteSnapshot, self).get_parser(prog_name)
        parser.add_argument("id", help="The ID of the server")
        parser.add_argument("snapshotID", help="The ID of the snapshot")
        return parser

    def take_action(self, args):
        cli = client.get_client_from_options(
            self._cmd_options)
        srv_cli = cli.get_client_for_server(args.id)
        srv_cli.delete_snapshot(args.snapshotID)
