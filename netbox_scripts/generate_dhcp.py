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
        vlan_id = 1031 + i

        if i<4:
            row = "e"
            rack = i+1
        else:
            row = "f"
            rack = i-3

        vlan_name = f"private1-{row}{rack}-eqiad"
        vlan = nb.ipam.vlans.get(name=vlan_name)
        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)

        print(f"        { vlan_name }:")
        for prefix in prefixes:
            pfx_obj = ipaddress.ip_network(prefix)
            if pfx_obj.version == 4:
                print(f"          ipv4: {prefix}")
            else:
                print(f"          ipv6: {prefix}")

        i += 1


if __name__=="__main__":
    main()

