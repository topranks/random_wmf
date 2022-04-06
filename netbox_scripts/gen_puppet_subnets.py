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

    i = 0
    while i<8:
        vlan_id = 1039 + i
        i += 1

        vlan = nb.ipam.vlans.get(group_id=13, vid=vlan_id)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)

        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            print(f"                    {pfx} #{vlan.name}")


if __name__=="__main__":
    main()

