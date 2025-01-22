#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import ipaddress
import argparse

import requests

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
        host_part_charlen = (128 - network.prefixlen) // 4
        network_chars = chars[:-host_part_charlen]
        revchars = network_chars[::-1]
        print(f"{network}: {'.'.join(revchars)}.ip6.arpa.")






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
    # Make a dict keyed by the prefix from this data and return
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

