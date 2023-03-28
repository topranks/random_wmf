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

    devices = nb.dcim.devices.filter(name__isw='lsw', site='codfw')
    for device in devices:
        if not device.name.startswith('lsw1'):
            new_name = f"{device.name.replace('lsw', 'lsw1')}"
            device.name = new_name
            device.save()


if __name__=="__main__":
    main()

