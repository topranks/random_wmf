#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

racks = ['c8', 'd5', 'e4', 'f4']

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    hosts = nb.dcim.devices.filter(role_id=1, status="active", name__isw="cloud", site_id=6)
    
    for host in hosts:
        if host.rack.name not in ['C8', 'D5', 'E4', 'F4']:
            print(f"{host.name} - {host.rack.name} - {host.primary_ip4}")

if __name__=="__main__":
    main()

