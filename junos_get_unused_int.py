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

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
parser.add_argument('-d', '--device', help='Device startswith', required=True, type=str)
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    if args.key:
        nb_key = args.key
    else:
        nb_key = getpass(prompt="Netbox API Key: ")
    nb = pynetbox.api(nb_url, nb_key)

    nb_device = nb.dcim.devices.get(name__isw=args.device)
    nb_ints = set(map(str, nb.dcim.interfaces.filter(device_id=nb_device.id)))

    dev_pri_ip = nb.ipam.ip_addresses.get(nb_device.primary_ip.id)

    junos_dev = get_junos_dev(dev_pri_ip.dns_name)
    filter_xml = "<interfaces/>"
    config = junos_dev.rpc.get_config(options={'format':'json'}, filter_xml=filter_xml)

    if type(config) != dict:
        print("ERROR: Config returned not in JSON format, JunOS version too old?")
        sys.exit(1)


    phys_int_regex = '^ge-|^xe-|^et-|^ae|^lo0|^fxp|^em'
    dev_ints = set()
    for interface in config['configuration']['interfaces']['interface']:
        if re.match(phys_int_regex, interface['name']):
            dev_ints.add(interface['name'])
        if "unit" in interface:
            for unit in interface['unit']:
                if unit['name'] != 0 or not re.match(phys_int_regex, interface['name']):
                    dev_ints.add(f"{interface['name']}.{unit['name']}")

    junos_dev.close()

    print("\nInterfaces on device but not in Netbox:")
    for int_name in (dev_ints - nb_ints):
        print(int_name)


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
