#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

devices = {
    'lvs2011': 'eno12399np0',
    'lvs2012': 'eno12399np0',
    'lvs2013': 'eno12409np1',
    'lvs2014': 'eno12409np1'
}

vlans = range(2021, 2036)

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    for vlan_id in range(2021, 2036):
        vlan = nb.ipam.vlans.get(vid=vlan_id)
        # vlan_row = vlan.name.split('-')[1][0]
        v4_pfx = nb.ipam.prefixes.get(vlan_id=vlan.id, family=4)

        network = ipaddress.ip_network(v4_pfx.prefix)
        print(f"ping -c 2 {network[1]}")

        '''
        print(f'  {vlan.name}:')
        print(f'    id: "{vlan.vid}"')
        print(f"    netmask: '255.255.255.0'")
        print(f"    iface:")
        for device_name, row_a_int in devices.items():
            new_ip = v4_pfx.available_ips.create()
            new_ip.description=f"{device_name} {row_a_int} vlan{vlan.vid}"
            new_ip.status='reserved'
            new_ip.save()
            new_ip_obj = ipaddress.ip_interface(new_ip.address)
            print(f"      {device_name}: '{row_a_int}:{new_ip_obj.ip}'")
        '''


if __name__=="__main__":
    main()

