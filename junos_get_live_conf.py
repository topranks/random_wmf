#!/usr/bin/python3

import pynetbox

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

from getpass import getpass
import argparse
import os
import sys
import re

from pathlib import Path
import json

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
parser.add_argument('-d', '--outputdir', help='Directory for output YAML files', default='junos_configs')
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    if args.key:
        nb_key = args.key
    else:
        nb_key = getpass(prompt="Netbox API Key: ")
    nb = pynetbox.api(nb_url, nb_key)

    p = Path(args.outputdir)
    p.mkdir(exist_ok=True)

    device_roles = ['cr']
    device_statuses = ['active', 'staged']

    for role in device_roles:
        nb_devices = nb.dcim.devices.filter(role=role)
        for nb_device in nb_devices:
            if str(nb_device.status).lower() not in device_statuses:
                continue
            dev_pri_ip = nb.ipam.ip_addresses.get(nb_device.primary_ip.id)
            junos_dev = get_junos_dev(dev_pri_ip.dns_name)
            filter_xml = "<protocols><bgp/></protocols>"
            config = junos_dev.rpc.get_config(options={'format':'json'}, filter_xml=filter_xml)

            with open(f"{args.outputdir}/{nb_device.name}", "w") as new_file:
                new_file.write(json.dumps(config))
                print(f"Saved JSON config for {nb_device.name}.")

            junos_dev.close()

def get_junos_dev(dev_name):
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
