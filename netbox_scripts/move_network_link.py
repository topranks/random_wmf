#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-f', '--file', help='Name of file with space separated list of hostnames and ints', type=str, default="move_ints.txt")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

'''
Input data example:

asw-b1-codfw ge-1/0/0	cloudsw1-b1-codfw ge-0/0/0
asw-b1-codfw ge-1/0/12	cloudsw1-b1-codfw ge-0/0/22
asw-b1-codfw ge-1/0/2	cloudsw1-b1-codfw ge-0/0/1
asw-b1-codfw ge-1/0/6	cloudsw1-b1-codfw ge-0/0/3
'''

def main():
    nb_url = "https://{}".format(args.netbox)
    global nb
    nb = pynetbox.api(nb_url, token=args.key)

    with open(args.file, "r") as input_file:
        for line in input_file.readlines():
            splitline = line.split()
            old_device = nb.dcim.devices.get(name=splitline[0])
            old_int = nb.dcim.interfaces.get(device_id=old_device.id, name=splitline[1])
            old_cable = old_int.cable
            new_device = nb.dcim.devices.get(name=splitline[2])
            new_int_name = splitline[3]
            new_int = nb.dcim.interfaces.get(device_id=new_device.id, name=new_int_name)

            print(f"Moving {old_device.name} {old_int.name} to {new_device.name} {new_int_name}...")

            # Create new int if needed
            if not new_int:
                new_int = create_new_int(new_int_name, new_device, old_int)

            # Set interface enabled and mtu
            new_int.enabled = old_int.enabled
            if new_int.enabled:
                if old_int.mtu:
                    new_int.mtu = old_int.mtu
                elif not old_int.type.value == 'virtual':
                    new_int.mtu = 9192

            # Move current connection if needed
            if old_int.cable:
                new_cable = move_cable(old_int, new_int)

            # Copy L2 stuff
            if old_int.mode:
                copy_vlans(old_int, new_int)

            # Check if it has children / sub-interfaces, if so move them too
            old_int_children = list(nb.dcim.interfaces.filter(device_id=old_device.id, parent_id=old_int.id))
            for subint in old_int_children:
                move_subint(subint, new_int)

            new_int.save()
            move_ips(old_int, new_int)
            reset_int(old_int)
            print("")


def reset_int(old_int):
    """ 'resets' interface by deleting it and then making a new one with same name - lazy! """
    int_type = old_int.type.value
    int_name = old_int.name
    device_id = old_int.device.id
    old_int.delete()
    reset_int = nb.dcim.interfaces.create(device=device_id, name=int_name, type=int_type)
    reset_int.enabled = False
    reset_int.save()
    print(f"    Reset {reset_int.device.name} {int_name} to defaults and set to disabled.")


def move_ips(old_int, new_int):
    ips = nb.ipam.ip_addresses.filter(interface_id=old_int.id)
    for ip in ips:
        ip.assigned_object_id = new_int.id
        if ip.dns_name:
            newint_dnsname = new_int.name.replace('/', '-').replace('.', '-')
            oldint_dnsname = old_int.name.replace('/', '-').replace('.', '-')
            splitdns = ip.dns_name.split('.')
            dnsname_one = splitdns[0]
            dnsname_two = splitdns[1]
            dns_suffix = splitdns[2:]
            if old_int.device.name == dnsname_two and oldint_dnsname == dnsname_one:
                # Old interface had DNS name based on normal pattern, udpate with new int and device name
                new_dns_name = f"{newint_dnsname}.{new_int.device.name}.{'.'.join(dns_suffix)}"
                print(f"    Chaning DNS entry for {ip} from {ip.dns_name} to {new_dns_name}... ", end="")
                ip.dns_name = new_dns_name
                print("done.")
            else:
                print(f"    Not updating DNS for {ip} - existing name {ip.dns_name} doesn't match pattern.")

        ip.save()
        print(f"    Moved {ip} from {old_int.device.name} {old_int.name} to {new_int.device.name} {new_int.name}")


def move_subint(old_subint, new_int):
    unit_id = old_subint.name.split(".")[-1]
    new_subint_name = f"{new_int}.{unit_id}"
    new_subint = create_new_int(new_subint_name, new_int.device, old_subint)
    new_subint.parent = new_int.id
    copy_vlans(old_subint, new_subint)
    move_ips(old_subint, new_subint)
    old_subint.delete()


def copy_vlans(old_int, new_int):
    print(f"    Setting {new_int.name} mode to {old_int.mode.value} and copying vlans... ", end='')
    new_int.mode = old_int.mode.value
    new_int.save()
    untagged_vlan = None
    if old_int.untagged_vlan:
        untagged_vlan = old_int.untagged_vlan.id
    new_int.untagged_vlan = untagged_vlan
    new_int.tagged_vlans = [vlan.id for vlan in old_int.tagged_vlans]
    print("done.")


def create_new_int(name, device, old_int):
    """ Creates new interfae on device with same base properties as old_int """
    new_int = nb.dcim.interfaces.create(device=device.id, name=name, type=old_int.type.value, enabled=True)
    new_int.description = old_int.description
    new_int.mgmt_only = old_int.mgmt_only
    if old_int.vrf:
        new_int.vrf = old_int.vrf.id
    new_int.save()
    print(f"    Created int {name} on {device.name}")
    return new_int


def move_cable(old_int, new_int):
    cable_color = old_int.cable.color
    cable_type = old_int.cable.type
    cable_label = old_int.cable.label
    termination = old_int.link_peer
    # Something of a hack?  needs to be dcim.interface or dcim.frontport
    termination_type = f"dcim.{termination.endpoint.name.rstrip('s').replace('-', '').lower()}"
   
    print(f"    Deleting cable {old_int.cable}")
    old_int.cable.delete()

    print(f"    Creating cable from {new_int.device.name} {new_int.name} - {termination.device.name} {termination.name}... ", end='')
    new_cable = nb.dcim.cables.create(termination_a_type='dcim.interface', termination_a_id=new_int.id,
        termination_b_type=termination_type, termination_b_id=termination.id, color=cable_color, 
        type=cable_type, status='connected', label=cable_label)
    print("done.")
    return new_cable


if __name__=="__main__":
    main()

