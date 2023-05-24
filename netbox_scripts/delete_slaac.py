#!/usr/bin/python3

import argparse
import pynetbox
import json

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    v6_ips = nb.ipam.ip_addresses.filter(family=6)

    for ip in v6_ips:
        print(dir(ip))
        print(ip.address.ip.bits())
        break

if __name__=="__main__":
    main()

