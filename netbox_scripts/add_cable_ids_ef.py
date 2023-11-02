#!/usr/bin/python3

import argparse
import pynetbox
import sys
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


# example input:
# ssw1-f1-eqiad et-0/0/4 lsw1-e5-eqiad et-0/0/55 202308009
# ssw1-f1-eqiad et-0/0/5 lsw1-e6-eqiad et-0/0/55 202308010
# ssw1-f1-eqiad et-0/0/6 lsw1-e7-eqiad et-0/0/55 202308011

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open('cable_ids.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            splits = line.split()
            leaf = splits[2]
            interface = splits[3]
            cable_id = splits[-1]

            nb_leaf = nb.dcim.devices.get(name=leaf)
            nb_int = nb.dcim.interfaces.get(device_id=nb_leaf.id, name=interface)
            cable = nb.dcim.cables.get(id=nb_int.connected_endpoint.cable)
            cable.label = cable_id
            cable.save()
            print(f"{leaf} {interface} {cable.label}")

if __name__=="__main__":
    main()

