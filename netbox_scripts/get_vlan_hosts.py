#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

vlan_id = 1120

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    vlan = nb.ipam.vlans.get(vid=vlan_id)

    interfaces = nb.dcim.interfaces.filter(vlan_id=vlan.id)

    for interface in interfaces: 
        if interface.connected_endpoint:
            print(f"{interface.connected_endpoint.device.name:<30} {interface.connected_endpoint.name}")


if __name__=="__main__":
    main()

