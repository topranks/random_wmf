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

    device = nb.dcim.devices.get(name='ssw1-f1-eqiad')
    interfaces = nb.dcim.interfaces.filter(device_id=device.id, name__isw="et")
    for interface in interfaces:
        new_name = interface.name.replace("et", "et-")
        interface.name = new_name
        interface.save()


if __name__=="__main__":
    main()

