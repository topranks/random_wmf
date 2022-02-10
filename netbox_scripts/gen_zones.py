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

    v4_pfx = {}
    v6_pfx = {}

    vlan_id = 1031
    while vlan_id<1047:
        vlan = nb.ipam.vlans.get(group_id=13, site_id=eqiad_site.id, vid=vlan_id)
        print(vlan)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)
        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            if type(pfx) == ipaddress.IPv4Network:
              v4_pfx[vlan.name] = pfx
            else:
              v6_pfx[vlan.name] = pfx
            
        vlan_id += 1

    print("")

    for vlan_name, ip_net in v4_pfx.items():
        rev_octets = str(ip_net.network_address).split(".")[0:3][::-1]
        zonefile = ".".join(rev_octets) + ".in-addr.arpa"
        originstr = ".".join(rev_octets[0:2])
        print(f"; {ip_net} - {vlan_name}")
        print(f"$ORIGIN {originstr}.@Z")
        print("; See https://wikitech.wikimedia.org/wiki/DNS/Netbox")
        print(f"$INCLUDE netbox/{zonefile}")
        print("")

    for vlan_name, ip_net in v6_pfx.items():
        rev_nibbles = str(ip_net.network_address.exploded).split(":")[0:4][::-1]
        rev_rev_nibbles = []
        for nibble in rev_nibbles:
            rev_rev_nibbles.append(nibble[::-1])

        originstr = ".".join(rev_rev_nibbles[0])

        concat = "".join(rev_rev_nibbles)
        zonefile = ".".join(concat) + ".ip6.arpa"

        print(f"; {vlan_name} ({ip_net})")
        print(f"$ORIGIN {originstr}.@Z")
        print("; See https://wikitech.wikimedia.org/wiki/DNS/Netbox")
        print(f"$INCLUDE netbox/{zonefile}")
        print("")

if __name__=="__main__":
    main()

