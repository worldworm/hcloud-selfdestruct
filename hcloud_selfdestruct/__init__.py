''' cli tool to self destruct a hetzner cloud server '''
import argparse
import socket
import os
import apprise
from hcloud import Client


class HcloudSelfDestruct:
    ''' main class '''

    def __init__(self, api_token):
        self.api_token = api_token
        self.server_id = None
        self.apprise_id = None
        self.server = None

    def detect_server_instance(self, servers):
        ''' detect server instance '''
        hostname = socket.gethostname()
        ip_address = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
        for server in servers:
            if server.public_net.ipv4.ip == ip_address and server.name == hostname:
                return server
        else:  # pylint: disable=useless-else-on-loop
            self.notify("could not identify")
            raise Exception("Could not identify server instance. Please specify server id.")

    def get_server_object(self):
        ''' get server object '''
        client = Client(token=self.api_token)
        if self.server_id:
            self.server = client.servers.get_by_id(self.server_id)
        else:
            servers = client.servers.get_all()
            self.server = self.detect_server_instance(servers)

    def notify(self, action):
        ''' notify '''
        if self.apprise_id:
            apprise_obj = apprise.Apprise()
            apprise_obj.add(self.apprise_id)
            apprise_obj.notify(
                body=f"{action} server{'' if not self.server else f': {self.server.name}'}",
                title="hcloud-selfdestruct",
            )

    def destroy(self):
        ''' destroy server '''
        self.get_server_object()
        self.notify("destroying")
        self.server.delete()

    def shutdown(self):
        ''' shutdown server '''
        self.get_server_object()
        self.notify("shutting down")
        self.server.shutdown()


def main():
    ''' main function '''
    argparser = argparse.ArgumentParser(description="cli tool to self destruct a hetzner cloud server")
    argparser.add_argument("--api-token",
                           "--api",
                           "--token",
                           type=str,
                           required=True,
                           help="hetzner cloud api token")
    argparser.add_argument("--server-id",
                           "--server",
                           "--id",
                           type=int,
                           required=False,
                           help="server id")
    argparser.add_argument("--apprise-id",
                           "--apprise",
                           "--notify",
                           type=str,
                           required=False,
                           help="apprise notification string")
    argparser.add_argument("--shutdown",
                           action="store_true",
                           help="just shutdown the server and not destroy it")
    args = argparser.parse_args()

    self_destroy = HcloudSelfDestruct(args.api_token)
    self_destroy.server_id = args.server_id
    self_destroy.apprise_id = args.apprise_id

    if args.shutdown:
        self_destroy.shutdown()
    else:
        self_destroy.destroy()
