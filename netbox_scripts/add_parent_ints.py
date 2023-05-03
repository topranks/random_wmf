#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

device_roles = ['cr', 'cloudsw', 'asw']

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    devices = nb.dcim.devices.filter(role=device_roles, status="active")
    for device in devices:
        if device.virtual_chassis:
            continue
        print(f"{device.name}")
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)
        int_dict = {}
        for interface in interfaces:
            int_dict[interface.name] = interface

        for int_name, nb_int in int_dict.items():
            if int_name.startswith("lo") or int_name.startswith("irb") or int_name.startswith("gr"):
                continue
            if "." in int_name:
                changed = False
                print(f"  {device.name} - {int_name}")
                parent_int_name = int_name.split(".")[0]
                if parent_int_name in int_dict:
                    # Get and set parent interface and port modes
                    parent_int = int_dict[parent_int_name]
                    if (not nb_int.parent) or nb_int.parent.id != parent_int.id:
#                       nb_int.parent = parent_int.id
                       print(f"    set {device.name} {nb_int.name} parent interface to {parent_int.name}")
                    if (not parent_int.mode) or parent_int.mode.value != 'tagged':
#                        parent_int.mode = 'tagged'
#                        parent_int.save()
                        print(f"    set {device.name} {parent_int.name} to mode tagged")
                        changed = True
                    if (not nb_int.mode) or nb_int.mode.value != "access":
#                        nb_int.mode = 'access'
                        changed = True
                        print(f"    set {device.name} {nb_int.name} to mode access")

                    # Get and set vlans on ports
                    vlan_id = int(int_name.split(".")[-1])
                    vlan = nb.ipam.vlans.get(vid=vlan_id, site_id=device.site.id)
                    if vlan:
                        if vlan not in parent_int.tagged_vlans:
    #                        parent_int.tagged_vlans.add(vlan.id)
                            changed = True
                            print(f"    added vlan id {vlan.vid} to tagged vlans on {device.name} {parent_int.name}")
                        if (not nb_int.untagged_vlan) or nb_int.untagged_vlan.id != vlan.id:
                            changed = True
    #                        nb_int.untagged_vlan = vlan.id
                            print(f"    set {device.name} {nb_int.name} untagged vlan id to {vlan.vid}")
                    else:
                        print(f"    802.1q tag {vlan_id} not a vlan at site {device.site.slug} - not setting on ports")

                    if changed:
                        pass
#                        parent_int.save()
#                        nb_int.save()
                else:
                    print(f"    ERROR: {int_name} defined but none called {parent_int_name} exists.")

        print()

if __name__=="__main__":
    main()

