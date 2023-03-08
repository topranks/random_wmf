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

    devices = ["lsw1-e1-eqiad", 
                "lsw1-f1-eqiad"]

    for device_name in devices:
        device = nb.dcim.devices.get(name=device_name)
        print(device)

        interfaces = nb.dcim.interfaces.filter(device=device_name)
        for interface in interfaces:
            print(interface)
            print(dir(interface))
            

if __name__=="__main__":
    main()

