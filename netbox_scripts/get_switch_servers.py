#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-s', '--switch', help='Switch name', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    device = nb.dcim.devices.get(name__isw=args.switch)
    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for interface in interfaces:
        if interface.connected_endpoint_type == "dcim.interface" and interface.connected_endpoint.device.device_role.slug == "server" and interface.untagged_vlan:
            print(f"{interface.name} - {interface.connected_endpoint.device.name}")
            

if __name__=="__main__":
    main()

