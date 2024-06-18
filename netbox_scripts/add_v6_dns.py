#!/usr/bin/python3

import argparse
import pynetbox

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('--hosts', help='String to match the start of host names on', required=True, type=str)
parser.add_argument('-d', '--dryrun', help='Toggle to dry-run and make no actual changes', action='store_true')
args = parser.parse_args()

def main():
    """ Sets the dns_name field for a device's primary_ip6 object to the same as 
        that on the primary_ip4 if there is none already.

        Input is a string that can be full hostname or just the start to match a range
    """

    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    hosts = nb.dcim.devices.filter(name__isw=args.hosts, status='active')
    for host in hosts:
        if host.primary_ip6 and not host.primary_ip6.dns_name:
            if not args.dryrun:
                host.primary_ip6.dns_name = host.primary_ip4.dns_name
                host.primary_ip6.save()
            print(f"Updated DNS entry for {host.name} IP {host.primary_ip6} to {host.primary_ip4.dns_name}")
            
if __name__=="__main__":
    main()

