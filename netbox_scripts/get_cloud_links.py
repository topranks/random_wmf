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

    with open('cloud_hosts.txt', 'r') as myfile:
        for line in myfile.readlines():
            device_name = line.split()[0]
            device = nb.dcim.devices.get(name=device_name)
            interfaces = nb.dcim.interfaces.filter(device_id=device.id, mgmt_only=False)
            for interface in interfaces:
                if interface.connected_endpoint:
                    print(f"{device.name} - {interface.name} {interface.connected_endpoint.device.name} {interface.connected_endpoint.name}")

            print("")


if __name__=="__main__":
    main()

