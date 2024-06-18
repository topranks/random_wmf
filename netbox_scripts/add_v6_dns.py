#!/usr/bin/python3

import argparse
import pynetbox

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('--hosts', help='String to match the start of host names on', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    hosts = nb.dcim.devices.filter(name__isw=args.hosts)
    for host in hosts:
        if not host.primary_ip6.dns_name:
            host.primary_ip6.dns_name = host.primary_ip4.dns_name
            host.primary_ip6.save()
            print(f"Updated DNS entry for {host.name} IP {host.primary_ip6} to {host.primary_ip6.dns_name}")
            
if __name__=="__main__":
    main()

