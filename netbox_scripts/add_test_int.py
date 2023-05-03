#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

#    new_int = nb.dcim.interfaces.create(device=4567, name="ge-0/0/2", mtu=9192, type='10gbase-x-sfpp')

    device = nb.dcim.devices.get(name="cloudsw1-b1-codfw")

    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for interface in interfaces:
        print(interface.name)
        print(dir(interface))
        break


if __name__=="__main__":
    main()

