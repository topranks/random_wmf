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

    for vlan_id in range(2021, 2036):
        vlan = nb.ipam.vlans.get(vid=vlan_id)
        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)
        print(f"        {vlan.name}:")
        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            if type(pfx) == ipaddress.IPv4Network:
                ipv4_str = f"          ipv4: {pfx}"
            else:
                ipv6_str = f"          ipv6: {pfx}"

        print(ipv4_str)
        print(ipv6_str)


if __name__=="__main__":
    main()

