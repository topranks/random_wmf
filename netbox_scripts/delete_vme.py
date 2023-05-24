#!/usr/bin/python3

import argparse
import pynetbox
import json

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    vme_ints = nb.dcim.interfaces.filter(name__isw='vme')

    for vme_int in vme_ints:
        print(f"{vme_int.device.name} {vme_int.name}")

if __name__=="__main__":
    main()

