#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


#device_roles = ["asw", "cloudsw", "cr"]
device_roles = ["cr"]


def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    cloudsw = nb.dcim.devices.get(name='cloudsw1-b1-codfw')
    vlan = nb.ipam.vlans.get(vid=2151, site='codfw')
    with open("cloudsw_ints.txt", "r") as input_file:
        for line in input_file.readlines():
            new_sw_int = nb.dcim.interfaces.get(device_id=cloudsw.id, name=line.split()[5])

            new_sw_int.mode = 'tagged'
            new_sw_int.tagged_vlans.append(vlan.id)
            new_sw_int.save()

            print(f"{new_sw_int} - {new_sw_int.untagged_vlan} - {new_sw_int.tagged_vlans}")



if __name__=="__main__":
    main()

