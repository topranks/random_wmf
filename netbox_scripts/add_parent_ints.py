#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


#device_roles = ["asw", "cloudsw", "cr"]
device_roles = ["cr"]


def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    devices = nb.dcim.devices.filter(role=device_roles, status="active")

    for device in devices:
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)
        int_dict = {}
        for interface in interfaces:
            int_dict[interface.name] = interface

        for int_name, nb_int in int_dict.items():
            if int_name.startswith("lo"):
                continue
            if "." in int_name:
                print(f"{device.name} - {int_name}")
                parent_int_name = int_name.split(".")[0]
                if parent_int_name in int_dict:
                    vlan_id = int(int_name.split(".")[-1])
                    vlan = nb.ipam.vlans.get(vid=vlan_id, site_id=device.site.id)
                    parent_int = int_dict[parent_int_name]
                    parent_int.mode ='tagged'
                    if vlan.id not in parent_int.tagged_vlans:
                        parent_int.tagged_vlans.append(vlan.id)
                    parent_int.save()
                    nb_int.mode = 'access'
                    nb_int.untagged_vlan = vlan.id
                    nb_int.parent = (parent_int.id)
                    nb_int.save()
                else:
                    print(f"ERROR: {int_name} defined but none called {parent_int} exists.")


        break

if __name__=="__main__":
    main()

