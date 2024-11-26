#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import ipaddress
import argparse

import requests

parser = argparse.ArgumentParser(description='Reverse zone delegation helper')
parser.add_argument('-p', '--prefixes', help='Commas-separated list of IPv6 subnets', required=True)
parser.add_argument('-d', '--dnsrepo', help='Path to zonefiles or templates in dns repo', default='/home/cmooney/repos/dns/templates')
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
args=parser.parse_args()

def main():
    # Get list of zones we are auth for from dns repo zone file names
    path = args.dnsrepo
    zone_filenames = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.arpa')]
    reverse_zones = {}
    for zone_name in zone_filenames:
        subnet = get_ip_subnet(zone_name)
        reverse_zones[subnet] = zone_name

    zonefile_content = {}
    for network_str in args.prefixes.split(","):
        network = ipaddress.ip_network(network_str)
        if network.prefixlen != 64:
            print("ERROR: {network} is not valid, needs to be /64 prefix.") 
            sys.exit(1)

        zone_name = get_zone(network, reverse_zones)
        if zone_name not in zonefile_content:
            zonefile_content[zone_name] = {}
        origin, include = get_include(network, zone_name)
        if origin not in zonefile_content[zone_name]:
            zonefile_content[zone_name][origin] = []
        zonefile_content[zone_name][origin].append({
            'include': include,
            'prefix': str(network)
        })

    # Get netbox info for descriptions
    nb_data = get_netbox_info()

    for zonefile_name, origin_data in zonefile_content.items():
        print(f"\n\n**** {zonefile_name} ****\n")
        for origin_line, includes in origin_data.items():
            for include in includes:
                try:
                    if nb_data[include['prefix']]['vlan']:
                        print(f"; Vlan {nb_data[include['prefix']]['vlan']['vid']} - {nb_data[include['prefix']]['vlan']['name']}")
                    elif nb_data[include['prefix']]['description']:
                        print(f"; {nb_data[include['prefix']]['description']}")
                except KeyError as e:
                    print(f"### ERROR with prefix {network} - not found in nb_data")
                print(origin_line)
                print(include['include'])

    print()

def get_zone(ip_network, reverse_zones):
    """ Gets zone name reverse records for a given IP subnet should go in """
    for zone_network, zone_name in reverse_zones.items():
        if zone_network.version != ip_network.version:
            continue
        if zone_network.supernet_of(ip_network):
            return zone_name


def get_include(reverse_network, zone_name):
    """ Gets the $ORIGIN statement needed in the given zone file, and the  """
    full_reverse = reverse_network.network_address.reverse_pointer.split(".")
    
    include_file = ".".join(full_reverse[16:])
    origin = f"$ORIGIN {include_file.replace(zone_name, '')}@Z"
    include_line = f"$INCLUDE netbox/{include_file}"

    return origin, include_line


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


def get_netbox_info():
    """ returns dict of data about the particular prefixes in netbox """
    prefix_query = """
        query nb_prefixes($prefixes: [String!]) {
          prefix_list(filters: {prefix: {in_list: $prefixes}}) {
            prefix
            vlan {
              name
              vid
            }
            description
          }
        }
    """
    prefix_query_vars = {
        "prefixes": args.prefixes.split(",")
    }


    query_result = get_graphql_query(prefix_query, prefix_query_vars)
    netbox_info = {}
    for prefix in query_result['prefix_list']:
        netbox_info[prefix['prefix']] = {
            'vlan': prefix['vlan'],
            'description': prefix['description']
        }

    return netbox_info


def get_graphql_query(query: str, variables: dict = None) -> dict:
    """Sends graphql query to netbox and returns JSON result as dict"""
    url = f"https://{args.netbox}/graphql/"
    headers = {
        'Authorization': f'Token {args.key}'
    }
    data = {"query": query}
    if variables is not None:
        data['variables'] = variables

    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


if __name__=="__main__":
    main()

