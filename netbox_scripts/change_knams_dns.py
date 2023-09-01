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


    with open('ips_cr3_knams.txt', 'r') as ip_file:
        for line in ip_file.readlines():
            ip = line.split()[0]

            nbip = nb.ipam.ip_addresses.get(address=ip)
            new_dns = nbip.dns_name.replace('cr3-knams', 'cr2-esams')
            nbip.dns_name = new_dns
            nbip.save()

if __name__=="__main__":
    main()

