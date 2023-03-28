#!/usr/bin/python3

import argparse
import pynetbox

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    device = nb.dcim.devices.get(name='cloudsw1-b1-codfw')
    new_sw_int = nb.dcim.interfaces.create(name='ge-0/0/17', device=device.id, type='1000base-t')


if __name__=="__main__":
    main()

