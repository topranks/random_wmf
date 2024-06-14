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
    
    ips = nb.ipam.ip_addresses.filter(parent='10.193.0.0/16')

    for ip in ips:
        if ip.dns_name:
            print(f"{ip} - {ip.dns_name}")


if __name__=="__main__":
    main()

