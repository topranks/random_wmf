#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress
from requests import Session

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-v', '--vlan', help='VLAN ID to get hosts belonging to', required=True, type=int)
parser.add_argument('--novm', help='Do not list virtual machines on the vlan', action="store_true", default=False)
args = parser.parse_args()

def main():
    nb = get_nb()

    v4_pfx = nb.ipam.prefixes.get(vlan_vid=args.vlan, family=4)

    ips = nb.ipam.ip_addresses.filter(parent=v4_pfx.prefix)

    vms = []    
    servers = []

    for ip in ips:
        if not args.novm and ip.assigned_object_type == "virtualization.vminterface":
            device = nb.virtualization.virtual_machines.get(ip.assigned_object.virtual_machine.id)
            vms.append(device.primary_ip4.dns_name)
            print(device.primary_ip4.dns_name)
            continue

        if ip.assigned_object_type == "dcim.interface" and ip.assigned_object:
            device = nb.dcim.devices.get(id=ip.assigned_object.device.id)
            if device.role.slug == "server":
                servers.append(device.primary_ip4.dns_name)
                print(device.primary_ip4.dns_name)

    if not args.novm:
        print("VMs:")
        print("\n".join(vms))
        print()
    print("Servers:")
    print("\n".join(servers))
    print()


    print(",".join(servers + vms))


def get_nb():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)
    http_session = Session()
    http_session.headers.update({'User-Agent': f'Cathal Script'})
    nb.http_session = http_session
    return nb 


if __name__=="__main__":
    main()

