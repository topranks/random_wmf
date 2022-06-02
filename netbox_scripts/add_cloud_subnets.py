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

#    ipv6_parent = "2620:0:861:100::/56"
#    pprefix = nb.ipam.prefixes.get(prefix=ipv6_parent)

    eqiad_site = nb.dcim.sites.get(slug="eqiad")

    i = 0
    while i<4:
        vlan_id = 1112 + i

        vlan_name = f"cloud-transit{i+7}-eqiad"

        new_vlan = nb.ipam.vlans.create(site=eqiad_site.id,
                                vid=vlan_id,
                                name=vlan_name,
                                group=13)

        subnet = f"172.31.255.{i * 2}/31"

        v4_subnet = nb.ipam.prefixes.create(prefix=subnet,
                                            site=eqiad_site.id,
                                            vlan=new_vlan.id,
                                            description = vlan_name)

        print(f"{vlan_id} {vlan_name} {subnet}")
        i += 1

if __name__=="__main__":
    main()

