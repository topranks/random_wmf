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
    'lvs2013': {'a': 'eno12409np1', 'b': 'enp152s0f0np0'},
    'lvs2014': {'a': 'eno12409np1', 'b': 'enp152s0f0np0'}
}

vlans = range(2021, 2036)

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    print("|LVS|Parent Int|New Int|Vlan Name|IPv4 Subnet|")
    for vlan_id in range(2021, 2036):
        vlan = nb.ipam.vlans.get(vid=vlan_id)
        vlan_row = vlan.name.split('-')[1][0]
        v4_pfx = nb.ipam.prefixes.get(vlan_id=vlan.id, family=4)

        for device_name, device_ints in devices.items():
            device = nb.dcim.devices.get(name=device_name)
            lvs_int = nb.dcim.interfaces.get(device_id=device.id, name=device_ints[vlan_row])
            print(f"|{device_name}|{lvs_int.name}|vlan{vlan.vid}|{vlan.name}|{v4_pfx}|")

            



if __name__=="__main__":
    main()

