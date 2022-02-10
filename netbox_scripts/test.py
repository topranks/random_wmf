#!/usr/bin/python3

import argparse
import pynetbox
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

    device=nb.dcim.devices.get(name='lsw1-e2-eqiad')

    print(dir(device))
    sys.exit(0)


    interfaces=nb.dcim.interfaces.filter(device_id=device.id)

    pattern = "0/0/48"

    for interface in interfaces:
        if re.search(f"^.*{pattern}$", interface.name):
            print(interface.connected_endpoint)
        else:
            print(interface.connected_endpoint)

#            print(f"{pattern} is NOT in {interface.name} on {device.name}")
    

if __name__=="__main__":
    main()

