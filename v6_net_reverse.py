#!/usr/bin/python3

import ipaddress
import argparse

parser = argparse.ArgumentParser(description='Reverse zone delegation helper')
parser.add_argument('-p', '--prefix', help='IPv6 subnet to show reverse zones for', required=True)
args=parser.parse_args()

def main():
    """Returns a list of DNS zone names that cover a given IPv6 subnet"""
    prefix = ipaddress.ip_network(args.prefix)
    if prefix.prefixlen % 4 == 0:
        networks = [prefix]
    else:
        # Supplied prefix was not at nibble boundary, get the multiple smaller nets that will cover
        closest_boundary = prefix.prefixlen + (4 - (prefix.prefixlen % 4))
        networks = list(prefix.subnets(new_prefix=closest_boundary))

    for network in networks:
        chars = network.network_address.exploded.replace(':', '')
        # Strip off the last N characters based on prefixlen (i.e. the "host" bits in this subnet)
        host_part_charlen = (128 - network.prefixlen) // 4
        network_chars = chars[:-host_part_charlen]
        # Reverse the remaining chars as that's how we write reverse PTR zones
        revchars = network_chars[::-1]
        print(f"{network}: {'.'.join(revchars)}.ip6.arpa.")

if __name__=="__main__":
    main()
