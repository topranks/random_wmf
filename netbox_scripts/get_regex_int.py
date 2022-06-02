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

#    device=nb.dcim.devices.get(name='asw-a1-codfw')
    device=nb.dcim.devices.get(name='asw1-b12-drmrs')

    print(device)

    if device.virtual_chassis:
        print(device.vc_position)


#    interfaces = nb.dcim.interfaces.filter(device_id=device.id, name="ge-1/0/8")

#    for interface in interfaces: 
#        print(dir(interface))


if __name__=="__main__":
    main()

