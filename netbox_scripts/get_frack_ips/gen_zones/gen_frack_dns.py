#!/usr/bin/python3

import argparse
import pynetbox
from getpass import getpass
import ipaddress
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', type=str, default='')
args = parser.parse_args()

# Dict to store data we grab from netbox
zone_data = {
    '10.in-addr.arpa': { 'records': {}, 'type': 'PTR' },
    'frack.eqiad.wmnet': { 'records': {}, 'type': 'A' },
    'mgmt.frack.eqiad.wmnet': { 'records': {}, 'type': 'A' },
    'frack.codfw.wmnet': { 'records': {}, 'type': 'A' },
    'mgmt.frack.codfw.wmnet': { 'records': {}, 'type': 'A' }
}

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    # Dict to store data we grab from netbox
    zone_data = {
        '10.in-addr.arpa': { 'records': {}, 'type': 'PTR' },
        'frack.eqiad.wmnet': { 'records': {}, 'type': 'A' },
        'mgmt.frack.eqiad.wmnet': { 'records': {}, 'type': 'A' },
        'frack.codfw.wmnet': { 'records': {}, 'type': 'A' },
        'mgmt.frack.codfw.wmnet': { 'records': {}, 'type': 'A' }
    }

    # Get the fr-tech vlans and from there get each attached subnet
    frack_vlans = nb.ipam.vlans.filter(tenant='fr-tech')
    for vlan in frack_vlans:
        ip_subnets = nb.ipam.prefixes.filter(vlan_id=vlan.id)
        for ip_subnet in ip_subnets:
            # Get all the IPs assigned from this subnet
            nb_addresses = nb.ipam.ip_addresses.filter(parent=str(ip_subnet), status='active')
            for nb_address in nb_addresses:
                ip_addr = ipaddress.ip_interface(nb_address).ip
                # A Record:
                fwd_zone, fwd_label = get_record_data(nb_address.dns_name)
                zone_data[fwd_zone]['records'][fwd_label] = str(ip_addr)
                # PTR Record:
                rev_label = ".".join(ip_addr.reverse_pointer.split(".")[0:3])
                zone_data['10.in-addr.arpa']['records'][rev_label] = f"{nb_address.dns_name}."

    # Write to output files
    Path("output").mkdir(exist_ok=True)
    for zone_name, zone_info in zone_data.items():
        record_type = zone_info['type']
        with open(f'output/{zone_name}', 'w') as zone_file:
            for dns_label, dns_record in zone_info['records'].items():
                zone_file.write(f"{dns_label:23} IN    {record_type:3}     {dns_record}\n")


def get_record_data(dns_name):
    """ Finds longest matching zone that dns_name could be part of and returns dns_name
        split into the parent_zone part and the RR record label part accordingly """
    zone_labels = 0
    parent_zone = ''
    # Loop over all the zone names we statically defined at the top
    for zone_name in zone_data.keys():
        if zone_name in dns_name:
            # The dns_name could fit into this one, compare to see if it's longest/most specific match
            num_labels = len(zone_name.split("."))
            if num_labels > zone_labels:
                zone_labels = num_labels
                parent_zone = zone_name

    # Calculate local RR label within the zone by stripping off the last N labels
    total_labels = len(dns_name.split('.'))
    rr_label = ".".join(dns_name.split('.')[0:(total_labels-zone_labels)])
    return parent_zone, rr_label
    

if __name__=="__main__":
    main()

