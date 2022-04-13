#!/usr/bin/python3

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

import argparse
import pynetbox

import platform
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', required=True, type=str)
parser.add_argument('-d', '--devices', help='Device startswith', required=True, type=str)
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    nb_devices = nb.dcim.devices.filter(name__isw=args.devices, status="active")
    for device in nb_devices:
        print(f"{device.name}")
        ip_addr = nb.ipam.ip_addresses.get(device.primary_ip.id)
        junos_dev = get_device(ip_addr.dns_name)
        config = junos_dev.rpc.get_config(options={'format':'json'})['configuration']
        try:
            for interface in config['protocols']['router-advertisement']['interface']:
                print(f"    {interface['name']}")
        except KeyError:
            pass
        print("")

        junos_dev.close()


def get_device(dev_name):
    # Initiates NETCONF session to router
    try:
        device = Device(dev_name, username=os.getlogin(), ssh_config=args.sshconfig, port=22)
        device.open()
    except ConnectError as err:
        print(f"Cannot connect to device: {err}")
        sys.exit(1)

    # Get config object
    device.bind(config=Config)

    return device


if __name__ == '__main__':
    main()
