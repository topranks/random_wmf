#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-f', '--file', help='Name of file with space separated list of hostnames and ints', type=str, default="move_ints.txt")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

'''
Input data example:

asw-b1-codfw ge-1/0/0	cloudsw1-b1-codfw ge-0/0/0
asw-b1-codfw ge-1/0/12	cloudsw1-b1-codfw ge-0/0/22
asw-b1-codfw ge-1/0/2	cloudsw1-b1-codfw ge-0/0/1
asw-b1-codfw ge-1/0/6	cloudsw1-b1-codfw ge-0/0/3
'''

def main():
    nb_url = "https://{}".format(args.netbox)
    global nb
    nb = pynetbox.api(nb_url, token=args.key)

    device = nb.dcim.devices.get(name='ssw1-e1-eqiad')
    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for interface in interfaces:
        if not interface.name.startswith('et'):
            continue
        int_dnsname = interface.name.replace('/', '-').replace('.', '-')
        ips = nb.ipam.ip_addresses.filter(interface_id=interface.id)
        for ip in ips:
            splitname = ip.dns_name.split('.')
            old_int_dnsname = splitname[0]
            old_device_name = splitname[1]
            dns_suffix = splitname[2:]
            new_dns_name = f"{int_dnsname}.{device.name}.{'.'.join(dns_suffix)}"
            if ip.dns_name != new_dns_name:
                ip.dns_name = new_dns_name
                ip.save()
                print(f"{new_dns_name} done.")

if __name__=="__main__":
    main()

