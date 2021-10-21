#!/usr/bin/python3

import argparse
import pynetbox
import string
import wikitextparser as wtp
import sys
import ipaddress
import re

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-s', '--site', help='Netbox site name', type=str, required=True)
parser.add_argument('-r', '--row', help='Row name/number (used to search rack-group)', type=str, required=True)
parser.add_argument('-l', '--listfile', help='File with list of servers/types', type=str, required=True)
parser.add_argument('-i', '--ignore', help='Ignore servers with connections only to swithches with given prefix', type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    server_types = []
    with open(args.listfile, 'r') as listfile:
        server_types = listfile.readlines()

    for server_type in server_types:
        if re.search('\d+$', server_type.rstrip("\n")):
            print(server_type.rstrip("\n"))

    site = nb.dcim.sites.get(slug=args.site)
    if site:
        racks = nb.dcim.racks.filter(site_id=site.id)
        rack_groups = set()
        for rack in racks:
            if rack.group.name.upper().endswith("ROW {}".format(args.row.upper())):
                rack_group = nb.dcim.rack_groups.get(rack.group.id)
                servers = nb.dcim.devices.filter(rack_group_id=rack_group.id, status="active", role="server")
                server_names = []
                for server in servers:
                    for server_type in server_types:
                        if server.name.startswith(server_type.rstrip("\n")):
                            print(server.name)

    else:
        print("No site \"{}\" found.. make sure to use correct slug as in Netbox.".format(args.site))
        sys.exit(1)

if __name__=="__main__":
    main()

