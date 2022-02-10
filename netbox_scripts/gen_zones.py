#!/usr/bin/python3

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

    # You can pre-add networks as shown below as required.
    v4_pfx = {"drmrs_loopbacks_interconnects": ipaddress.ip_network('10.136.127.0/24')}
    v6_pfx = {"cr1-eqiad_to_lsw1-e1-eqiad":  ipaddress.ip_network('2620:0:861:fe07::/64'),
                "cr2-eqiad_to_lsw1-f1-eqiad": ipaddress.ip_network('2620:0:861:fe08::/64'),
                "cr2-eqdfw_to_asw1-b13-drmrs": ipaddress.ip_network('2620:0:860:fe0a::/64')
    }

    # Or if the subnets are associated with Vlans specify the range here
    vlan_id = 1031
    while vlan_id<1033:
        vlan = nb.ipam.vlans.get(group_id=13, vid=vlan_id)
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
        rev_hextets = str(ip_net.network_address.exploded).split(":")[0:4][::-1]
        rev_nibbles = []
        for hextet in rev_hextets:
            rev_nibbles.append(hextet[::-1])

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

