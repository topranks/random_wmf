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

    leaf_names = ["lsw1-f5-eqiad", "lsw1-f6-eqiad", "lsw1-f7-eqiad"]
    spine_names = ['ssw1-e1-eqiad', 'ssw1-f1-eqiad']
    spines = []
    for spine_name in spine_names:
        spines.append(nb.dcim.devices.get(name=spine_name))

    pprefix = nb.ipam.prefixes.get(prefix="10.64.129.0/24")
    spine_port_num = 12

    for leaf_name in leaf_names:
        leaf = nb.dcim.devices.get(name=leaf_name)

        # Create all the interfaces in this case
        for port_num in range(48, 56):
            new_int = nb.dcim.interfaces.create(device=leaf.id, name=f"et-0/0/{port_num}", 
                        type="100gbase-x-qsfp28", enabled=False)
            print(f"{leaf.name} - {new_int.name}")

        # Create cable to each spine
        for spine_num in range(len(spines)):
            spine = spines[spine_num]
            spine_port = nb.dcim.interfaces.get(device_id=spines[spine_num].id, name=f"et-0/0/{spine_port_num}")
            leaf_port = nb.dcim.interfaces.get(device_id=leaf.id, name=f"et-0/0/{(56 - len(spines)) + spine_num}")
            spine_port.enabled = True
            spine_port.mtu = 9192
            spine_port.save()
            leaf_port.enabled = True
            leaf_port.mtu = 9192
            leaf_port.save()

            print(f"Connect {spine.name} {spine_port.name} - {leaf.name} {leaf_port.name}...")
            new_cable = nb.dcim.cables.create(termination_a_type="dcim.interface", termination_b_type="dcim.interface",
                termination_a_id=spine_port.id, termination_b_id=leaf_port.id, color="ffeb3b", type="smf", status='planned',
                label=f"changeme_{leaf_port.id}")

            # Assign IPv4 underlay range to port
            link_prefix = pprefix.available_prefixes.create({"prefix_length": 31})
            link_prefix.description=f"{leaf.name} {leaf_port.name} link to {spine.name} {spine_port.name}"
            link_prefix.save()

            print(f"Assigned {link_prefix} for link.")

            link_ips = link_prefix.available_ips.list()
            print(f"spine: {link_ips[0]}, leaf: {link_ips[1]}")

            spine_ip = nb.ipam.ip_addresses.create(address=str(link_ips[0]),
                assigned_object_type="dcim.interface",
                assigned_object_id=spine_port.id,
                dns_name=f"{spine_port.name.replace('/', '-')}.{spine.name}.eqiad.wmnet")

            leaf_ip = nb.ipam.ip_addresses.create(address=str(link_ips[1]),
                assigned_object_type="dcim.interface",
                assigned_object_id=leaf_port.id,
                dns_name=f"{leaf_port.name.replace('/', '-')}.{leaf.name}.eqiad.wmnet")

        # Increment spine port num for next leaf link
        spine_port_num += 1
        print()

            
if __name__=="__main__":
    main()

