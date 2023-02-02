""" helper script to test hcloud-selfdestruct """
import os
import argparse
from time import sleep
import warnings
import paramiko
from termcolor import cprint
from hcloud import Client, APIException
from hcloud.server_types.domain import ServerType
from hcloud.images.domain import Image

# due to using paramiko WarningPolicy() to ignore host key errors
warnings.simplefilter("ignore")


class E2ESelfDestruct:
    """ main class """

    def __init__(self, api_token):
        self.api_token = api_token
        self.hcloud = Client(self.api_token)
        self.ssh_private_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ssh_key")
        self.ssh_public_key = None
        self.hcloud_server_responses = []
        self.generate_ssh_key()
        self.upload_ssh_key()

    def generate_ssh_key(self):
        """ generate ssh key """
        cprint("generating ssh key", "dark_grey")
        key = paramiko.RSAKey.generate(4096)
        key.write_private_key_file(self.ssh_private_key_file, password=None)
        self.ssh_public_key = f"{key.get_name()} {key.get_base64()}"

    def upload_ssh_key(self):
        """ upload ssh key to hetzner cloud """
        cprint("uploading ssh key to hetzner cloud", "dark_grey")
        self.hcloud.ssh_keys.create(name="E2ESelfDestruct", public_key=self.ssh_public_key)

    def get_cloud_init_from_file(self):
        """ get cloud-init from cloud-init.yml """
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloud-init.yml"), "r", encoding="utf-8") as file:
            user_data = file.read()
        return user_data

    def deploy_server(self):
        """ deploy multiple hcloud server """
        cloud_init = self.get_cloud_init_from_file()
        ssh_key = self.hcloud.ssh_keys.get_by_name("E2ESelfDestruct")
        print("deploying servers...")
        for image in ["ubuntu-22.04", "fedora-37", "debian-11", "centos-stream-9", "rocky-9"]:
            print(f"    {image}")
            response = self.hcloud.servers.create(
                name=f"hcloud-selfdestruct-test-{image.split('.', maxsplit=1)[0]}", server_type=ServerType(name="cx11"),
                image=Image(name=image), user_data=cloud_init, ssh_keys=[ssh_key])
            self.hcloud_server_responses.append(response)

    def wait_for_ssh_server(self):
        """ wait for ssh server to be available """
        cprint("waiting for ssh-server to boot...", "dark_grey")
        for response in self.hcloud_server_responses:
            cprint(f"    {response.server.name}", "dark_grey")
            ssh_available = False
            while ssh_available is False:
                try:
                    ssh_con = paramiko.client.SSHClient()
                    ssh_con.set_missing_host_key_policy(paramiko.WarningPolicy())
                    paramiko.AutoAddPolicy()
                    ssh_key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key_file, password=None)
                    ssh_con.connect(response.server.public_net.ipv4.ip, username="root", look_for_keys=False, pkey=ssh_key, timeout=60)
                    ssh_con.close()
                    ssh_available = True
                except paramiko.ssh_exception.NoValidConnectionsError:
                    sleep(5)

    def wait_for_cloud_init(self):
        """ wait for cloud-init to install hcloud-selfdestruct """
        cprint("waiting for cloud-init to finish...", "dark_grey")
        for response in self.hcloud_server_responses:
            cprint(f"    {response.server.name}", "dark_grey")
            ssh_con = paramiko.client.SSHClient()
            ssh_con.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh_key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key_file, password=None)
            ssh_con.connect(response.server.public_net.ipv4.ip, username="root", look_for_keys=False, pkey=ssh_key, timeout=60)
            _stdin, _stdout, _stderr = ssh_con.exec_command("""
                                                            until command -v hcloud-selfdestruct &> /dev/null
                                                            do
                                                                sleep 5
                                                            done
                                                            """, timeout=180)
            _stdout.read().decode("utf-8")
            ssh_con.close()

    def trigger_selfdestruct(self):
        """ test hcloud-selfdestruct """
        print("running selfdestruct...")
        for response in self.hcloud_server_responses:
            print(f"    {response.server.name}")
            ssh_con = paramiko.client.SSHClient()
            ssh_con.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh_key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key_file, password=None)
            ssh_con.connect(response.server.public_net.ipv4.ip, username="root", look_for_keys=False, pkey=ssh_key, timeout=60)
            _stdin, _stdout, _stderr = ssh_con.exec_command("python3 --version")
            cprint(f"        python version: {_stdout.read().decode('utf-8').strip()}", attrs=["underline"])
            _stdin, _stdout, _stderr = ssh_con.exec_command(f"hcloud-selfdestruct --api-token {self.api_token}")
            cprint("        selfdestruct triggered", "dark_grey")
            ssh_con.close()

    def check_for_existing_servers(self):
        """ check for existing servers """
        print("check for existing servers...")
        sleep(5)
        for response in self.hcloud_server_responses:
            try:
                self.hcloud.servers.get_by_id(response.server.id)
                cprint(f"    {response.server.name} still exists", "red")
            except APIException:
                cprint(f"    {response.server.name} not found", "green")

    def cleanup(self):
        """ cleanup"""
        self.hcloud.ssh_keys.delete(self.hcloud.ssh_keys.get_by_name("E2ESelfDestruct"))
        os.remove(self.ssh_private_key_file)
        cprint("ssh key deleted", "dark_grey")


def main():
    """ main function """
    # pylint: disable=duplicate-code
    argparser = argparse.ArgumentParser(description="helper script to test hcloud-selfdestruct")
    argparser.add_argument("--api-token",
                           "--api",
                           "--token",
                           type=str,
                           required=True,
                           help="hetzner cloud api token")
    # pylint: enable=duplicate-code
    args = argparser.parse_args()

    e2e = E2ESelfDestruct(args.api_token)
    e2e.deploy_server()
    e2e.wait_for_ssh_server()
    e2e.wait_for_cloud_init()
    e2e.trigger_selfdestruct()
    e2e.check_for_existing_servers()
    e2e.cleanup()


if __name__ == "__main__":
    main()
