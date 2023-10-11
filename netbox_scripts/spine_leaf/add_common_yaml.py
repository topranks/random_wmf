#!/usr/bin/python3

import argparse
import pynetbox
import sys
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


# input is a list of hostnames on separate lines

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open('new_devs.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            device = nb.dcim.devices.get(name=line.rstrip())
            lo5000 = nb.dcim.interfaces.get(device_id=device.id, name="lo0.5000")
            ip4 = nb.ipam.ip_addresses.get(interface_id=lo5000.id, family=4)
            ip6 = nb.ipam.ip_addresses.get(interface_id=lo5000.id, family=6)
            print(f"  {device.name}:")
            print(f"    ipv4: {ip4.address.split('/')[0]}")
            print(f"    ipv6: {ip6.address.split('/')[0]}")
            print(f"    site: {device.site.slug}")
            print(f"    role: l3sw")

if __name__=="__main__":
    main()

