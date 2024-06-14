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

    with open('dns_records.txt', 'r') as myfile:
        for line in myfile.readlines():
            ip = line.strip().split()[-1]
            nb_ip = nb.ipam.ip_addresses.get(address=ip)
            nb_ip.dns_name = ''
            nb_ip.save()
            print(nb_ip)

if __name__=="__main__":
    main()

