#!/usr/bin/python3

import argparse
import pynetbox
import sys
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


# input is a list of hostnames on separate lines

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open('new_devs.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            device = nb.dcim.devices.get(name=line.rstrip())
            print(f"{device.primary_ip4.dns_name};juniper;up;")

if __name__=="__main__":
    main()

