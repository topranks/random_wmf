#!/usr/bin/python3

import ipaddress
import argparse

import sys

parser = argparse.ArgumentParser(description='Reverse zone delegation helper')
parser.add_argument('prefix')
args=parser.parse_args()

def main():
    try:
        prefix = ipaddress.ip_network(args.prefix)
    except ValueError:
        # Not a valid CIDR network
        ip_addr = ipaddress.ip_interface(args.prefix)
        prefix = ip_addr.network
        print(f"WARNING: {ip_addr} is not a valid network address, using {prefix}")

    if prefix.prefixlen % 4 == 0:
        networks = [prefix]
    else:
        # Supplied prefix was not at nibble boundary, get the multiple smaller nets that will cover
        closest_nibble_pfxlen = prefix.prefixlen + (4 - (prefix.prefixlen % 4))
        networks = list(prefix.subnets(new_prefix=closest_nibble_pfxlen))

    for network in networks:
        chars = network.network_address.exploded.replace(':', '')
        # Strip off the last N characters based on prefixlen (i.e. the "host" bits in this subnet)
        host_part_charlen = (128 - network.prefixlen) // 4
        network_chars = chars[:-host_part_charlen]
        # Reverse the remaining chars as that's how we write reverse PTR zones
        revchars = network_chars[::-1]
        print(f"{'.'.join(revchars)}.ip6.arpa.    ({network})")

if __name__=="__main__":
    main()

