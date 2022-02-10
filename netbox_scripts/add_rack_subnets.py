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

    ipv6_parent = "2620:0:861:100::/56"
    pprefix = nb.ipam.prefixes.get(prefix=ipv6_parent)

    eqiad_site = nb.dcim.sites.get(slug="eqiad")

    i = 0
    while i<8:
        vlan_id = 1039 + i

        if i<4:
            row = "e"
            rack = i+1
        else:
            row = "f"
            rack = i-3

        vlan_name = f"analytics1-{row}{rack}-eqiad"

        new_vlan = nb.ipam.vlans.create(site=eqiad_site.id,
                                vid=vlan_id,
                                name=vlan_name,
                                group=13)

        v6_subnet = pprefix.available_prefixes.create({"prefix_length": 64})
        v6_subnet.description = vlan_name
        v6_subnet.site = eqiad_site.id
        v6_subnet.vlan = new_vlan.id
        v6_subnet.save()

        v4_subnet = nb.ipam.prefixes.create(prefix=f"10.64.{138 + i}.0/24",
                                            site=eqiad_site.id,
                                            vlan=new_vlan.id,
                                            description = vlan_name)

        print(vlan_name) 
        i += 1


if __name__=="__main__":
    main()

