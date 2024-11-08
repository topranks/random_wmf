#!/usr/bin/python3

import argparse
import pynetbox
from getpass import getpass
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', type=str, default='')
parser.add_argument('-f', '--file', help='Output YAML file to write to (default hosts.yaml)', type=str, default='hosts.yaml')
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    frack_data = {}
    for site in ('codfw', 'eqiad'):
        frack_hosts = nb.dcim.devices.filter(site=site, 
                                             tenant='fr-tech', 
                                             status=('active', 'planned'), 
                                             role='server')
        for host in frack_hosts:
            bond_int = nb.dcim.interfaces.get(device_id=host.id, name='bond0')
            if bond_int == None:
                print(f"ERROR: {host} is in Netbox but no interface bond0 exists.")
                continue
            if bond_int.mac_address == None:
                print(f"Skipping {host} as no MAC address is configured on bond0.")
                continue
    
            int_ip = nb.ipam.ip_addresses.get(interface_id=bond_int.id)
            if int_ip == None:
                print(f"ERROR: {host} is in Netbox but there is no IP on interface bond0.")
            
            frack_data[host.name] = {}
            frack_data[host.name]['macaddress'] = bond_int.mac_address
            frack_data[host.name]['ipaddress'] = int_ip.address.split('/')[0]

    with open(args.file, 'w') as outfile:
        yaml.dump(frack_data, outfile)
    print(f"\nWrote YAML output to {args.file}")
            

if __name__=="__main__":
    main()

