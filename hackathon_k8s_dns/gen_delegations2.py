#!/usr/bin/python3

import yaml
import ipaddress
from pathlib import Path

def main():
    with open('dns_reverse_zones.yaml', 'r') as myfile:
        zone_data = yaml.safe_load(myfile.read())
    # Build dict from reverse_zone_data using ipaddress.ip_network objects
    reverse_zones = {ipaddress.ip_network(pfx): zone for pfx, zone in zone_data.items()}
    # Dict with empty list for each zone to store the records we'll create
    zonefile_content = {reverse_zone: [] for reverse_zone in reverse_zones.values()}

    with open('dns_k8s_reverse_delegation.yaml', 'r') as myfile:
        k8s_clusters = yaml.safe_load(myfile.read())
    for cluster_name, cluster_data in k8s_clusters.items():
        for network_str in cluster_data['networks']:
            network = ipaddress.ip_network(network_str)
            if network.version == 4 and network.prefixlen not in (8, 16, 24):
                # IPv4 subnet is not at a dotted decimal boundary, break into multiple
                closest_boundary = network.prefixlen + (8 - (network.prefixlen % 8))
                delegate_networks = list(network.subnets(new_prefix=closest_boundary))
            else:
                # network is already at an octet or nibble boundary so no sub-division required
                delegate_networks = [network]

            for delegate_network in delegate_networks:
                zone_name = get_zone(delegate_network, reverse_zones)
                zone_label = get_zone_label(delegate_network, zone_name)
                zonefile_content[zone_name].append(f"; {cluster_name} {delegate_network}")
                for name_server in cluster_data['name_servers']:
                    zonefile_content[zone_name].append(f"{zone_label:<15} IN    NS    {name_server}.")

    write_entries(zonefile_content)


def write_entries(zonefile_content):
    """ Writes the output files to disk """
    Path("output").mkdir(exist_ok=True)
    for zone_name, zone_entries in zonefile_content.items():
        if zone_entries:
            with open(f'output/{zone_name}', 'w') as outfile:
                outfile.writelines(f"{zone_entry}\n" for zone_entry in zone_entries)


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

if __name__=="__main__":
    main()
