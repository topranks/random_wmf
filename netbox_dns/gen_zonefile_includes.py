#!/usr/bin/python3
import json

from os import listdir
from os.path import isfile, join
from pathlib import Path

import ipaddress
import argparse
import requests

parser = argparse.ArgumentParser(description='Netbox zonefile snippet/record generator')
parser.add_argument('-d',
                    '--dnsrepo',
                    help='Path to zonefiles or templates in Gerrit repo',
                    default='https://gerrit.wikimedia.org/r/plugins/gitiles/operations/dns/+/refs/heads/master/templates/'
                    )
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
args = parser.parse_args()

USER_AGENT = {
    "User-Agent": "Netbox DNS Zonefile Generator 1.0",
    "From": "infrastructure-foundation@wikimedia.org"
}


def dns_templates_names():
    # Read zonefile names from dns repo and generate a list of template names
    url = f"{args.dnsrepo}?format=json"
    response = requests.get(url, headers=USER_AGENT)

    # Do the little Gerrit dance to strip the broken first line of JSON that
    # Gerrit always output.
    data = response.text
    if data.startswith(")]}'"):
        data = response.text[4:]

    # Only return actual files, e.g. blobs and skip trees (directories).
    return [t["name"] for t in json.loads(data)["entries"] if t["type"] == "blob"]

def main():
    # Generate dicts with zone names to store entries for each zone
    templates = dns_templates_names()
    fwd_zone_names = [f for f in templates if not f.endswith('.arpa')]
    fwd_zone_entries = {zone_name: [] for zone_name in fwd_zone_names}
    rev_zone_entries = {f: [] for f in templates if f.endswith('.arpa')}
    # Dict keyed by ipaddress.ip_network objects with values of corresponding rev zone name
    rev_zone_subnets = {get_ip_subnet(zone_name): zone_name for zone_name in rev_zone_entries.keys()}

    # Iterate over IPs returned from Netbox
    nb_ips = get_netbox_ips()
    for nb_ip in nb_ips:
        ip_addr = ipaddress.ip_interface(nb_ip['address'])

        # Forward entry
        fqdn = nb_ip['dns_name']
        fwd_zone = get_fwd_zone(fqdn, fwd_zone_names)
        if fwd_zone is not None:
            record_type = 'A' if ip_addr.version == 4 else 'AAAA'
            label = fqdn.replace(f'.{fwd_zone}', '')
            fwd_zone_entries[fwd_zone].append(f"{label:40} IN {record_type:7} {ip_addr.ip.compressed}")

        # Reverse entry
        rev_zone = get_rev_zone(ip_addr, rev_zone_subnets)
        if rev_zone is None:
            print(f"Skipping reverse for {ip_addr} as it doesn't fit into any zone we are auth for")
            continue
        label = ip_addr.ip.reverse_pointer.replace(f".{rev_zone}", "")
        rev_zone_entries[rev_zone].append(f"{label:23} IN    PTR    {fqdn}.")

    write_files(fwd_zone_entries)
    write_files(rev_zone_entries)
    print("\nWrote output files into snippet dir.")


def write_files(zone_entries):
    """Writes contents of zone entries dicts to disk"""
    for zone_name, zone_records in zone_entries.items():
        if not zone_records:
            # We can skip this to create empty files if we wish
            continue

        # TODO - We should sort the entries so adjacent ones always are beside each other for diff
        Path("snippets").mkdir(exist_ok=True)
        with open(f"snippets/{zone_name}", "w") as outfile:
            outfile.write("$ORIGIN @Z\n")
            for zone_record in zone_records:
                outfile.write(f"{zone_record}\n")


def get_fwd_zone(fqdn, zone_names):
    """Returns zone name with most specific match for fqdn"""
    longest_match = 0
    matching_zone = None
    for zone_name in zone_names:
        if zone_name in fqdn and len(zone_name.split('.')) > longest_match:
            matching_zone = zone_name
            longest_match = len(zone_name.split('.'))
    return matching_zone


def get_rev_zone(ip_addr, rev_zone_subnets):
    """Gets the zone name that reverse records for a given IP should go in.
       We return the first match as we have no overlapping zones defined for 
       reverses (nor are we likely to have), so we don't need to find most specific"""
    for zone_network, zone_name in rev_zone_subnets.items():
        if zone_network.version == ip_addr.version and zone_network.supernet_of(ip_addr.network):
            return zone_name


def get_ip_subnet(zone_name):
    """Returns the IP subnet corresponding to a dns reverse zone name"""
    if zone_name.endswith('in-addr.arpa'):
        bits_per_label = 8
        num_labels = 4
        labels = zone_name.replace('.in-addr.arpa', '').split('.')
    elif zone_name.endswith('ip6.arpa'):
        bits_per_label = 4
        num_labels = 32
        labels = zone_name.replace('.ip6.arpa', '').split('.')

    # Reverse the labels as the zone name has them backwards to the IP
    labels.reverse()
    pfxlen = len(labels) * bits_per_label
    # Pad out the labels array with zeros to represent the full network address
    while len(labels) < num_labels:
        labels.append('0')

    if num_labels == 32:
        # IPv6: each label is one hex digit, we group into four to write the IP
        quartets = [''.join(labels[i:i+4]) for i in range(0, len(labels), 4)]
        return ipaddress.ip_network(f"{':'.join(quartets)}/{pfxlen}")
    else:
        # IPv4: labels are 0-255 already so we can use them directly
        return ipaddress.ip_network(f"{'.'.join(labels)}/{pfxlen}")


def get_netbox_ips() -> list:
    """Gets list of IPs in Netbox with dns_name attributes"""
    ip_query = """
        {
          ip_address_list(filters: { NOT: {dns_name:{exact:""} }}) {
            address
            dns_name
          }
        }
    """
    return get_graphql_query(ip_query)['ip_address_list']


def get_graphql_query(query: str) -> dict:
    """Sends graphql query to netbox and returns JSON result as dict"""
    url = f"https://{args.netbox}/graphql/"
    headers = {
        'Authorization': f'Token {args.key}'
    }
    headers.update(USER_AGENT)
    data = {"query": query}
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


if __name__ == "__main__":
    main()
