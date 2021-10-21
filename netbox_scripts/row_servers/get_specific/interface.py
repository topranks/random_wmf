#!/usr/bin/python3

import argparse
import pynetbox
import string
import wikitextparser as wtp
import sys
import ipaddress
import re

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    router = nb.dcim.devices.get(name='mr1-ulsfo')
    interfaces = nb.dcim.interfaces.filter(device_id=router.id)

    for interface in interfaces:
        print("{} - {} - {}".format(interface.name, interface.type.label, interface.type.value))

if __name__=="__main__":
    main()

