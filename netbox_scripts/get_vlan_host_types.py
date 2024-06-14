#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-v', '--vlan', help='VLAN ID to get hosts belonging to', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    vlans = nb.ipam.vlans.filter(name__isw=args.vlan)

    servers = []
    server_types = set()

    for vlan in vlans:
        print(f"{vlan.name}")
        v4_pfx = nb.ipam.prefixes.get(vlan_vid=vlan.vid, family=4)
        ips = nb.ipam.ip_addresses.filter(parent=v4_pfx.prefix)
        for ip in ips:
            if ip.assigned_object_type == "dcim.interface" and ip.assigned_object:
                device = nb.dcim.devices.get(id=ip.assigned_object.device.id)
                if device.device_role.slug == "server":
                    servers.append(device.name)
                    server_types.add(device.name.rstrip('0123456789'))

    print()
    for server_type in server_types:
        print(server_type)


if __name__=="__main__":
    main()

