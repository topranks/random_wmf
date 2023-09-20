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

            print(host.name)
            host_ints = nb.dcim.interfaces.filter(mgmt_only=False, device_id=host.id)
            update = True
            for interface in host_ints:
                # Get IP address to see if it is primary int or not
                int_ip = nb.ipam.ip_addresses.get(device_id=host.id, interface_id=interface.id, family=4)
                if int_ip:
                    int_ip_obj = ipaddress.ip_interface(int_ip.address)
                    if int_ip_obj in tendot and interface.connected_endpoint:
                        server_int = interface
                        switchport = interface.connected_endpoint
                        untagged_vlan = switchport.untagged_vlan.id
                        tagged_vlans = [vlan.id for vlan in switchport.tagged_vlans]
                    elif int_ip_obj in cloud_agg:
                        # Host already has connection to cloud-private
                        update = False

            if update:
                # Change server primary int to mode tagged with correct vlans, allocate IP for new vlan int
                print(f"  Changing {host.name} {server_int.name} to tagged.")
                server_int.mode = "tagged"
                server_int.untagged_vlan = untagged_vlan
                server_int.tagged_vlans = tagged_vlans
                server_int.save()
                
                # Create new interface
                print(f"  Creating vlan interface")
                new_vlan_int = nb.dcim.interfaces.create(device=host.id, name=f"vlan{nb_vlan.vid}", type="virtual",
                    enabled=True, mgmt_only=False, mode="access", untagged_vlan=nb_vlan.id, parent=server_int.id)

                new_ip = nb_prefix.available_ips.create()
                new_ip.assigned_object_type="dcim.interface"
                new_ip.assigned_object_id=new_vlan_int.id
                new_ip.dns_name=f"{host.name}.private.eqiad.wikimedia.cloud"
                new_ip.save()
                print(f"  Assigned {new_ip.address} to {host.name}")



if __name__=="__main__":
    main()

