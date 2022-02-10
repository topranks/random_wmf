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

    device = nb.dcim.devices.get(name="lsw1-e1-eqiad")

    print(device)

    interface = nb.dcim.interfaces.get(device_id=device.id, name="et-0/0/49")

    print(dir(interface.device))


if __name__=="__main__":
    main()

