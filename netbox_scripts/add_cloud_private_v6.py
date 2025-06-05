#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

from pynetbox.core.query import RequestError

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    parent_range = "172.20.5.0/24"

    prefixes = nb.ipam.prefixes.filter(within_include=parent_range)
    for prefix in prefixes:
        ips = nb.ipam.ip_addresses.filter(parent=prefix.prefix)
        v6_prefix = nb.ipam.prefixes.get(vlan_id=[prefix.vlan.id], family=6)
        v6_network = v6_prefix.prefix.split("/")[0]
        for ip in ips:
            # Skip if IP is connected to an interface and its not a server:
            if ip.assigned_object and ip.assigned_object_type == 'dcim.interface':
                connected_int = nb.dcim.interfaces.get(ip.assigned_object.id)
                device = nb.dcim.devices.get(connected_int.device.id)
                if device.role.slug != "server":
                    continue
            last_oct = int(ip.display.split("/")[0].split(".")[-1])
            new_ip_str = f"{v6_network}{last_oct}/64"
            try:
                new_ip = nb.ipam.ip_addresses.create(address=new_ip_str, dns_name=ip.dns_name, status='active')
            except RequestError:
                print(f"Skipping {new_ip_str} / {ip.dns_name} as v6 address is already assigned")
                continue
            if ip.assigned_object:
                new_ip.assigned_object_type="dcim.interface"
                new_ip.assigned_object_id=ip.assigned_object.id
            new_ip.save()
            print(f"Assigned {new_ip} as {new_ip.dns_name}")

if __name__=="__main__":
    main()

