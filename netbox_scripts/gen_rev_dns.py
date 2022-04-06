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

    subnets = ['10.64.128.0/23']

    for subnet in subnets:
        nb_ips = nb.ipam.ip_addresses.filter(parent=subnet)
        for ip in nb_ips:
            if ip.assigned_object:
                int_name = ip.assigned_object.name
                device_name = ip.assigned_object.device.display_name
                if ip.role:
                    if ip.role.label == "Loopback":
                        ip.dns_name = f"{int_name}-0.{device_name}.eqiad.wmnet"
                else:
                    ip.dns_name = f"{int_name.replace('/', '-')}.{device_name}.eqiad.wmnet"

                ip.save()

            else:
                print(ip)


if __name__=="__main__":
    main()

