#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    # TODO - this was for CR so used wikimedia.org for all, could check if it's part of 10/8 to decide to use wmnet instead

    with open('codfw_ips.txt', 'r') as ip_file:
        for line in ip_file.readlines():
            ip = line.strip()
            nbip = nb.ipam.ip_addresses.get(address=ip)
            interface = nb.dcim.interfaces.get(id=nbip.assigned_object_id)
            print(f"{nbip} - {nbip.dns_name} - {interface.name.replace('/', '-').replace('.', '-')}.{interface.device.name}.wikimedia.org")
            new_dns_name = f"{interface.name.replace('/', '-').replace('.', '-')}.{interface.device.name}.wikimedia.org"
            nbip.dns_name = new_dns_name
            nbip.save()

if __name__=="__main__":
    main()

