#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

racks = ['c8', 'd5', 'e4', 'f4']

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    tendot = ipaddress.ip_network('10.0.0.0/8')
    cloud_agg = ipaddress.ip_network('172.20.0.0/16')

    for rack in racks:
        vlan_name = f"cloud-private-{rack}-eqiad"
        nb_vlan = nb.ipam.vlans.get(name=vlan_name)

        nb_prefix = nb.ipam.prefixes.get(vlan_id=nb_vlan.id)

        nb_rack =  nb.dcim.racks.get(site="eqiad", name=rack.upper())

        hosts = nb.dcim.devices.filter(rack_id=nb_rack.id, role_id=1, status="active")
        for host in hosts:
            if (not host.name.startswith("cloud")) or host.name.startswith("cloudnet") or host.name.startswith("cloudgw") or host.name.startswith("cloudweb"):
                continue

            print(f"## {host.name}")
            host_ints = nb.dcim.interfaces.filter(mgmt_only=False, device_id=host.id)
            update = True
            for interface in host_ints:
                # Get IP address to see if it is primary int or not
                int_ip = nb.ipam.ip_addresses.get(device_id=host.id, interface_id=interface.id, family=4)
                if int_ip:
                    int_ip_obj = ipaddress.ip_interface(int_ip.address)
                    if int_ip_obj in cloud_agg:
                        # this is the one 
                        print(f"ip link add link {interface.parent} name {interface.name} type vlan id {interface.untagged_vlan.vid}")
                        print(f"ip addr add {int_ip_obj} dev {interface.name}")
                        print(f"ip route add 172.20.0.0/16 via {int_ip_obj.network[1]}")
                        print(f"ip route add 185.15.56.0/24 via {int_ip_obj.network[1]}")

            print()

if __name__=="__main__":
    main()

