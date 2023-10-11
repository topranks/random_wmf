#!/usr/bin/python3

import argparse
import pynetbox
import sys
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

# input is a list of hostnames on separate lines

parent = "msw1"

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    print("hieradata/common/monitoring.yaml:\n\n")
    with open('new_devs.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            print(f"  {line.rstrip()}:")
            print(f"    description: Equipment with {line.rstrip()} as uplink")

    print("\n\nmodules/netops/manifests/monitoring.pp:\n\n")
    with open('new_devs.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            nb_dev = nb.dcim.devices.get(name=line.strip())
            print(f"        '{line.strip()}.mgmt' => {{ ipv4 => '{nb_dev.primary_ip4.address.split('/')[0]}', parents => ['{parent}-{nb_dev.site.slug}'] }},")


if __name__=="__main__":
    main()

