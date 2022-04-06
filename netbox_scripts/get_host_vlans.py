#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

vlan_id = 1106
host_start = 'an-worker114'

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    hosts = nb.dcim.devices.filter(name__isw=host_start)

    print(f"Host                 Interface       Far Side                       Vlans")
    for host in hosts:
        interfaces = nb.dcim.interfaces.filter(device_id=host.id)
        for interface in interfaces:
            if interface.connected_endpoint:
                z_int = nb.dcim.interfaces.get(interface.connected_endpoint.id)
                tagged_vlans = ""
                if len(z_int.tagged_vlans) > 0:
                    for vlan in z_int.tagged_vlans:
                        tagged_vlans += f"{vlan.name} ({vlan.vid}), "
                    tagged_vlans = tagged_vlans.rstrip(", ")
                    if z_int.untagged_vlan:
                        print(f"{host.name:<20} {interface.name:<15} {interface.connected_endpoint.device.name + ':' + interface.connected_endpoint.name:<30} {z_int.untagged_vlan.name} ({z_int.untagged_vlan.vid}) | Tagged: {tagged_vlans}")
                    else:
                        print(f"{host.name:<20} {interface.name:<15} {interface.connected_endpoint.device.name + ':' + interface.connected_endpoint.name:<30} Tagged: {tagged_vlans}")
                elif z_int.untagged_vlan:
                    print(f"{host.name:<20} {interface.name:<15} {interface.connected_endpoint.device.name + ':' + interface.connected_endpoint.name:<30} {z_int.untagged_vlan.name} ({z_int.untagged_vlan.vid})")


            

    

if __name__=="__main__":
    main()

