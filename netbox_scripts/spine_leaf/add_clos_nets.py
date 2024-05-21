#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress
import yaml
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-y', '--yamlfile', help='YAML file with source info', required=True, type=str)
# TODO add switch to also add analytics nets
args = parser.parse_args()


def main():
    # Sure, I shouldn't do this.  I know.
    global nb, nb_subnets, site, vlan_group, input_data

    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open(args.yamlfile, 'r') as yamlfile:
        input_data = yaml.safe_load(yamlfile)

    # Get netbox objects for parent prefixes we make allocations from
    nb_subnets = {}
    for subnet_name, subnet in input_data['subnets'].items():
        nb_subnets[subnet_name] = nb.ipam.prefixes.get(prefix=subnet)
   
    site = nb_subnets['underlay_links'].site
    vlan_group = nb.ipam.vlan_groups.get(name="production", site=site.id)
 
    # Get netbox objects for spine switches 
    spines = []
    for spine_name in input_data['devices']['spine']:
        nb_spine = nb.dcim.devices.get(name=spine_name)
        print(f"\n{spine_name.upper()}")
        add_loopback_interface(nb_spine, 'lo0', 0, [nb_subnets['underlay_loopbacks']])
        add_loopback_interface(nb_spine, 'lo0.5000', 2, [nb_subnets['overlay_loopback4'], nb_subnets['overlay_loopback6']])
        spines.append(nb_spine)

    # Loop over leaf switches and add elements as needed
    spine_port = 0
    for leaf_name in input_data['devices']['leaf']:
        print(f"\n{leaf_name.upper()}")
        leaf = nb.dcim.devices.get(name=leaf_name)

        # Links, link subnets etc.
        # Increment spine port if current one is in list to skip
        while spine_port in input_data['skip_spine_int']:
            spine_port += 1

        for index, spine in enumerate(spines):
            add_spine_link(spine, leaf, spine_port, 55-index)

        spine_port += 1

        # Per-leaf subnet/vlan/irb int creation
        add_leaf_vlan('private1', leaf)

        # Leaf underlay loopback
        add_loopback_interface(leaf, 'lo0', 0, [nb_subnets['underlay_loopbacks']])
        # Leaf overlay loopback
        add_loopback_interface(leaf, 'lo0.5000', 2, [nb_subnets['overlay_loopback4'], nb_subnets['overlay_loopback6']])

    print("")


def add_loopback_interface(nb_device, int_name, vrf_id, parent_subnets):
    """ Adds loopback int to a device and assigns IPs from parent_subnets """

    # Check if it already exists
    loop_int = nb.dcim.interfaces.get(device_id=nb_device.id, name=int_name)
    if loop_int:
        print(f"    Interface {int_name} already exists on {nb_device.name}... skipping.")
        return

    print(f"    Creating interface {int_name} on {nb_device.name}...", end="")
    loop_int = nb.dcim.interfaces.create(device=nb_device.id, name=int_name, type='virtual')
    if vrf_id:
        loop_int.vrf = vrf_id
        loop_int.save()
    print(" done.")

    for prefix in parent_subnets:
        print(f"        Creating IP for {int_name} on {nb_device.name} from {prefix.prefix}...", end="")
        new_ip = prefix.available_ips.create()
        new_ip.assigned_object_type="dcim.interface"
        new_ip.assigned_object_id=loop_int.id
        new_ip.role = "loopback"
        new_ip.dns_name=f"{int_name.replace('.','-')}.{nb_device.name}.{site.slug}.wmnet"
        # Change mask to host one
        if new_ip.family.value == 4:
            new_ip.address=f"{new_ip.address.split('/')[0]}/32"
        else:            
            new_ip.address=f"{new_ip.address.split('/')[0]}/128"
        print(f" {new_ip}.")
        new_ip.save()

         
def get_next_vid(vlan_id):
    """ Returns next non-allocated vlan id in Netbox >= vlan_id """
    while True:
        nb_vlan = nb.ipam.vlans.get(vid=vlan_id)
        if not nb_vlan:
            return vlan_id
        else:
            vlan_id += 1
            

def add_spine_link(spine, leaf, spine_port, leaf_port):
    """ Takes NB object of a spine device, leaf device, and the port on each to connect
        together and adds the link, link subnet and attaches link IPs."""

    leaf_int = get_nb_int(leaf, f"et-0/0/{leaf_port}")
    leaf_int.mtu = 9192
    leaf_int.save()
    spine_int = get_nb_int(spine, f"et-0/0/{spine_port}")
    spine_int.mtu = 9182
    spine_int.save

    # Add connection between ports if needed
    if not leaf_int.connected_endpoint and not spine_int.connected_endpoint:
        print(f"    Adding link from {leaf.name} et-0/0/{leaf_port} to {spine.name} et-0/0/{spine_port}...", end="")
        new_cable = nb.dcim.cables.create(termination_a_type="dcim.interface", termination_b_type="dcim.interface",
                termination_a_id=spine_int.id, termination_b_id=leaf_int.id, color="ffeb3b", type="smf", status='planned')
        print(" done.")
    elif leaf_int.connected_endpoint and spine_int.connected_endpoint:
        # Quit if they are not connected to each other
        if leaf_int.connected_endpoint != spine_int:
            print(f"    ERROR: {leaf.name} et-0/0/{leaf_port} connection does not go to {spine.name} et-0/0/{spine_port}.  Quitting!")
            sys.exit(1)
    else:
        # One side has a connection and not the other - quit.
        print(f"    ERROR: {leaf.name} et-0/0/{leaf_port} connection does not go to {spine.name} et-0/0/{spine_port}.  Quitting!")
        sys.exit(1)

    # Add IP addressing to link
    add_link_ips(leaf_int, spine_int)


def get_nb_int(device, int_name):
    """ Returns netbox interface object on device with int_name, if it 
        doesn't already exist it will create it as QSFP28 """

    nb_int = nb.dcim.interfaces.get(device_id=device.id, name=int_name)
    if nb_int:
        if not nb_int.enabled:
            print(f"    Enabling {device.name} {int_name} and setting MTU to 9192...", end="")
            nb_int.enabled = True
            nb_int.mtu = 9192
            nb_int.save()
            print(" done.")
        return nb_int

    # Otherwise we create the int and return it
    print(f"    Creating {device.name} {int_name}...", end="")
    nb_int = nb.dcim.interfaces.create(device=device.id, name=int_name, mtu=9192, type='100gbase-x-qsfp28')
    print(" done.")
    return nb_int


def add_link_ips(leaf_int, spine_int):
    """ Allocate IP range for link and add to ports if needed """

    # Check that interfaces don't already have IPs, and either skip (both sides have) or quit (only one does)
    existing_spine_ips = list(nb.ipam.ip_addresses.filter(interface_id=spine_int.id))
    existing_leaf_ips = list(nb.ipam.ip_addresses.filter(interface_id=leaf_int.id))
    if existing_spine_ips and existing_leaf_ips:
        print(f"    {leaf_int.device.name} {leaf_int.name} and {spine_int.device.name} {spine_int.name} already have IPs, skipping.")
        return
    elif (existing_spine_ips and not existing_leaf_ips) or (not existing_spine_ips and existing_leaf_ips):
        print(f"    One side of {leaf_int.device.name} {leaf_int.name} and {spine_int.device.name} {spine_int.name} already has IPs... quitting!")
        sys.exit(1)
    
    # Allocate a new /31 prefix from underlay link range
    print(f"    Assigning link subnet for {leaf_int.device.name} {leaf_int.name} to {spine_int.device.name} {spine_int.name}...", end="")
    link_prefix = nb_subnets['underlay_links'].available_prefixes.create({"prefix_length": 31})
    link_prefix.description=f"{leaf_int.device.name} <-> {spine_int.device.name}"
    link_prefix.save()
    print(f" {link_prefix}.")

    # Assign an IP to each side
    link_ips = link_prefix.available_ips.list()

    print(f"      Adding {link_ips[0]} to {spine_int.device.name} {spine_int.name}...", end="")
    spine_ip = nb.ipam.ip_addresses.create(address=str(link_ips[0]),
        assigned_object_type="dcim.interface",
        assigned_object_id=spine_int.id,
        dns_name=f"{spine_int.name.replace('/', '-')}.{spine_int.device.name}.{site.slug}.wmnet")
    print(" done.")

    print(f"      Adding {link_ips[1]} to {leaf_int.device.name} {leaf_int.name}...", end="")
    leaf_ip = nb.ipam.ip_addresses.create(address=str(link_ips[1]),
        assigned_object_type="dcim.interface",
        assigned_object_id=leaf_int.id,
        dns_name=f"{leaf_int.name.replace('/', '-')}.{leaf_int.device.name}.{site.slug}.wmnet")
    print(" done.")


def add_leaf_vlan(vlan_type, leaf):
    """ Adds a new vlan, assigns IPv4 and IPv6 subnet to it and creates IRB on the Leaf for it """

    vlan_name = f"{vlan_type}-{leaf.rack.name.lower()}-{site.slug}"
    # Check if a vlan with this name exists 
    nb_vlan = nb.ipam.vlans.get(name=vlan_name)
    if nb_vlan:
        print(f"    {vlan_name} already exists - skipping.")
        return

    # Create vlan   
    vlan_id = get_next_vid(input_data['vlans']['vlan_start']) 
    print(f"    Creating vlan {vlan_name} with vid {vlan_id}...", end="")
    new_vlan = nb.ipam.vlans.create(site=site.id, vid=vlan_id, name=vlan_name, group=vlan_group.id, status="reserved")
    print(" done.")

    # Assign prefixes
    print(f"      Assigning IPv6 prefix for {vlan_name}...", end="")
    v6_subnet = nb_subnets['vlan6'].available_prefixes.create({"prefix_length": 64})
    v6_subnet.description = vlan_name
    v6_subnet.site = site.id
    v6_subnet.vlan = new_vlan.id
    v6_subnet.save()
    print(f"{v6_subnet}.")

    print(f"      Assigning IPv4 prefix for {vlan_name}...", end="")
    v4_subnet = nb_subnets['vlan4'].available_prefixes.create({"prefix_length": 24})
    v4_subnet.description = vlan_name
    v4_subnet.site = site.id
    v4_subnet.vlan = new_vlan.id
    v4_subnet.save()
    print(f"{v4_subnet}.")

    # Create IRB interface
    print(f"      Creating interface irb.{vlan_id} on {leaf.name}...", end="")
    irb_int = nb.dcim.interfaces.create(device=leaf.id, name=f"irb.{vlan_id}", 
        type='virtual', vrf=2, description=vlan_name)
    print(" done.")

    # Create GW IPs
    for prefix in [v6_subnet, v4_subnet]:
        print(f"        Creating GW for {vlan_name} from {prefix.prefix}...", end="")
        new_ip = prefix.available_ips.create()
        new_ip.assigned_object_type="dcim.interface"
        new_ip.assigned_object_id=irb_int.id
        new_ip.dns_name=f"irb-{vlan_id}.{leaf.name}.{site.slug}.wmnet"
        print(" done.")
        new_ip.save()


if __name__=="__main__":
    main()

