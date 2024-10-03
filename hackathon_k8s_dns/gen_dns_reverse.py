#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import ipaddress
import yaml

def main():
    path = '/home/cmooney/repos/dns/templates'
    zone_filenames = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.arpa')]
    zone_info = {}
    for zone_name in zone_filenames:
        subnet = get_ip_subnet(zone_name)
        zone_info[subnet] = zone_name

    with open('dns_reverse_zones1.yaml', 'w') as outfile:
        yaml.dump(zone_info, outfile)

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
        return str(ipaddress.ip_network(f"{':'.join(quartets)}/{pfxlen}"))
    else:
        return f"{'.'.join(elements)}/{pfxlen}"


if __name__=="__main__":
    main()

