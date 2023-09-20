#!/usr/bin/python3

import sys
import argparse
import pynetbox
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    # TODO: Needs to be adjusted depending on IPv6 parent prefixes
    # Works for 2620:0:860::/46, needs adjusting for thing in 2a02:ec80::/29

    # You can manually add pre-add networks as shown below as required.
    #v4_pfx = {"esams_new_loopback4": ipaddress.ip_network('10.80.127.0/24')}
    #v6_pfx = {"cr2-esams <-> cr1-drmrs": ipaddress.ip_network('2a02:ec80:300:fe09::/64'),
    #          "cr1-esams <-> cr2-drmrs": ipaddress.ip_network("2a02:ec80:300:fe0a::/64")}

    v4_pfx = {}
    v6_pfx = {}


    # Or if the subnets are associated with Vlans specify the range here
    for vlan_id in range(332, 333):
        vlan = nb.ipam.vlans.get(vid=vlan_id)
        print(vlan)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)
        for prefix in prefixes:
            if prefix.family.value == 4:
              v4_pfx[vlan.name] = ipaddress.ip_network(prefix.prefix)
            else:
              v6_pfx[vlan.name] = ipaddress.ip_network(prefix.prefix)
            
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
        rev_hextets = str(ip_net.network_address.exploded).split(":")[0:4][::-1]
        rev_nibbles = [hextet[::-1] for hextet in rev_hextets]
        
        originstr = ".".join(rev_nibbles[0])
        concat = "".join(rev_nibbles)
        zonefile = ".".join(concat) + ".ip6.arpa"

        print(f"; {vlan_name} ({ip_net})")
        print(f"$ORIGIN {originstr}.@Z")
        print("; See https://wikitech.wikimedia.org/wiki/DNS/Netbox")
        print(f"$INCLUDE netbox/{zonefile}")
        print("")

if __name__=="__main__":
    main()

