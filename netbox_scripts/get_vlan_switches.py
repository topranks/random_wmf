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

    nb_vlan = nb.ipam.vlans.get(vid=args.vlan)

    print(nb_vlan.name)


if __name__=="__main__":
    main()

