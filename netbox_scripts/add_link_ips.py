#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    devices = ["lsw1-e1-eqiad", 
                "lsw1-f1-eqiad"]

    parent_prefix = "10.64.129.0/24"


    for device_name in devices:
        device = nb.dcim.devices.get(name=device_name)
        print(device)


        pprefix = nb.ipam.prefixes.get(prefix=parent_prefix)

        interfaces = nb.dcim.interfaces.filter(device=device_name)
        for interface in interfaces:
            try:
                cable = nb.dcim.cables.get(interface.connected_endpoint.cable)
            except AttributeError:
                print(f"Interface {interface} has no connection... skipping.")
                continue

            if cable.termination_a.device.name == device_name:
                int_b = nb.dcim.interfaces.get(cable.termination_b_id)
                device_b = nb.dcim.devices.get(cable.termination_b.device.id)
            else:
                int_b = nb.dcim.interfaces.get(cable.termination_a_id)
                device_b = nb.dcim.devices.get(cable.termination_a.device.id)
            
            print(f"Device {device_name} {interface} is connected to {device_b} {int_b}")

            link_prefix = pprefix.available_prefixes.create({"prefix_length": 31})
            link_prefix.description=f"{device_name} {interface} link to {device_b} {int_b}"
            link_prefix.save()

            link_ips = link_prefix.available_ips.list()

            a_side_ip = nb.ipam.ip_addresses.create(address=str(link_ips[0]),
                                                    assigned_object_type="dcim.interface",
                                                    assigned_object_id=interface.id)
            print(a_side_ip)

            b_side_ip = nb.ipam.ip_addresses.create(address=str(link_ips[1]),
                                                    assigned_object_type="dcim.interface",
                                                    assigned_object_id=int_b.id)
            print(b_side_ip)
            


if __name__=="__main__":
    main()

