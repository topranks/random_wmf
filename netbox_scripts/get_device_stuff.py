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

    devices = nb.dcim.devices.filter(name__isw="lsw1")

    for device in devices:
        if "spare" in device.name:
            continue
        if "4" in device.name:
            continue
        mgmt_int = nb.dcim.interfaces.get(device_id=device.id, name="em0")
        ips = nb.ipam.ip_addresses.filter(interface_id=mgmt_int.id)
        print(f"'{ips[0].dns_name}'     => {{ ipv4    => '{ips[0].address.split('/')[0]}'}},")

if __name__=="__main__":
    main()

