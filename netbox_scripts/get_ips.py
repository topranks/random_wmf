#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-p', '--prefix', help='IP Prefix to search for', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    try:
        ip_obj = ipaddress.ip_network(args.prefix)
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)

    ips = nb.ipam.ip_addresses.filter(parent=args.prefix)

    print("IP         DNS      Description")
    for ip in ips:
        print("{} {} {}".format(ip, ip.dns_name, ip.description))
        

if __name__=="__main__":
    main()

