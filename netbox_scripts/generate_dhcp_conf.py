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
    while i<16:
        vlan_id = 1031 + i
        i += 1

        vlan = nb.ipam.vlans.get(group_id=13, vid=vlan_id)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)

        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            if type(pfx) == ipaddress.IPv4Network:
                print(f"# {vlan.name}")
                print(f"subnet {pfx.network_address} netmask {pfx.netmask} {{")
                print("    authoritative;")
                print("")
                print(f"    option subnet-mask {pfx.netmask};")
                print(f"    option broadcast-address {pfx[-1]};")
                print(f"    option routers {pfx[1]};")
                print("    option domain-name \"eqiad.wmnet\";")
                print("")
                print("    next-server 208.80.154.32; # install1003 (tftp server)")
                print("}")
                print("")




if __name__=="__main__":
    main()

