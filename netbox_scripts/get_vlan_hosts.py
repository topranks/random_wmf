#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-v', '--vlan', help='VLAN ID to get hosts belonging to', required=True, type=int)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    v4_pfx = nb.ipam.prefixes.get(vlan_vid=args.vlan, family=4)

    ips = nb.ipam.ip_addresses.filter(parent=v4_pfx.prefix)
    
    servers = []

    for ip in ips:
        if ip.assigned_object_type == "virtualization.vminterface":
            device = nb.virtualization.virtual_machines.get(ip.assigned_object.virtual_machine.id)
            servers.append(device.primary_ip4.dns_name)
        elif ip.assigned_object_type == "dcim.interface" and ip.assigned_object:
            device = nb.dcim.devices.get(id=ip.assigned_object.device.id)
            if device.device_role.slug == "server":
                servers.append(device.primary_ip4.dns_name)

    print("\n".join(servers))
    print()
    print(",".join(servers))


if __name__=="__main__":
    main()

