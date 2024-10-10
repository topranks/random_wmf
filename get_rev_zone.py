#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import ipaddress
import yaml
import argparse

import argparse

parser = argparse.ArgumentParser(description='Reverse zone delegation helper')
parser.add_argument('-p', '--prefix', help='CIDR prefix we want to delegate', required=True)
parser.add_argument('-d', '--dnsrepo', help='Path to zonefiles or templates in dns repo', default='/home/cmooney/repos/dns/templates')
args=parser.parse_args()


def main():
    # Get list of zones we are auth for from dns repo zone file names
    path = args.dnsrepo
    zone_filenames = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.arpa')]
    reverse_zones = {}
    for zone_name in zone_filenames:
        subnet = get_ip_subnet(zone_name)
        reverse_zones[subnet] = zone_name

    network = ipaddress.ip_network(args.prefix)
    if network.version == 4 and network.prefixlen not in (8, 16, 24):
        # IPv4 subnet is not at a dotted decimal boundary, break into multiple
        closest_boundary = network.prefixlen + (8 - (network.prefixlen % 8))
        delegate_networks = list(network.subnets(new_prefix=closest_boundary))
    elif network.version == 6 and (network.prefixlen % 4) != 0:
        closest_boundary = network.prefixlen + (4 - (network.prefixlen % 4))
        delegate_networks = list(network.subnets(new_prefix=closest_boundary))
    else:
        # network is already at an octet or nibble boundary so no sub-division required
        delegate_networks = [network]

    zonefile_content = []
    for delegate_network in delegate_networks:
        zone_name = get_zone(delegate_network, reverse_zones)
        zone_label = get_zone_label(delegate_network, zone_name)
        zonefile_content.append(f"{zone_label:<15} IN    NS    <name_server>")

    print(f"### {zone_name} ###")
    for line in zonefile_content:
        print(line)


def get_zone(ip_network, reverse_zones):
    """ Gets zone name reverse records for a given IP subnet should go in """
    for zone_network, zone_name in reverse_zones.items():
        if zone_network.version != ip_network.version:
            continue
        if zone_network.supernet_of(ip_network):
            return zone_name


def get_zone_label(delegate_network, zone_name):
    """ Gets the label to use for the NS entry within the given zone file """
    delegate_full_reverse = delegate_network.network_address.reverse_pointer.split(".")
    if delegate_network.version == 4:
        # We have up to 4 octets, each octet represents 8 bits
        slice_left = 4-(delegate_network.prefixlen//8)
    else:
        # We have up to 32 characters in the reverse entry, each is 1 hex digit so 4 bits
        slice_left = 32-(delegate_network.prefixlen//4)

    label_right_side = '.'.join(delegate_full_reverse[slice_left:])
    label = label_right_side.replace(f".{zone_name}", '')
    return label



def get_ip_subnet(zone_name):
    """ Returns the IP subnet corresponding to a dns reverse zone name """
    if zone_name.endswith('in-addr.arpa'):
        bits_per_element = 8
        max_elements = 4
        elements = zone_name.replace('.in-addr.arpa', '').split('.')
    elif zone_name.endswith('ip6.arpa'):
        bits_per_element = 4
        max_elements = 32
        elements = zone_name.replace('.ip6.arpa', '').split('.')

    elements.reverse()
    pfxlen = len(elements) * bits_per_element
    while len(elements) < max_elements:
        elements.append('0')

    if max_elements == 32:
        # Each 'element' is one hex digit but we need to group into four to create the IP
        quartets = [''.join(elements[i:i+4]) for i in range(0, len(elements), 4)]
        # Convert to ipaddress object and back again to minimize v6 addr
        return ipaddress.ip_network(f"{':'.join(quartets)}/{pfxlen}")
    else:
        return ipaddress.ip_network(f"{'.'.join(elements)}/{pfxlen}")


if __name__=="__main__":
    main()

