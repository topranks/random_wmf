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

    devices = ["lsw1-e5-eqiad",
               "lsw1-e6-eqiad", 
               "lsw1-e7-eqiad", 
               "lsw1-f5-eqiad", 
               "lsw1-f6-eqiad", 
               "lsw1-f7-eqiad"]

    underlay_prefix = nb.ipam.prefixes.get(prefix="10.64.128.0/24")
    overlay_prefix4 = nb.ipam.prefixes.get(prefix="10.64.146.0/24")
    overlay_prefix6 = nb.ipam.prefixes.get(prefix="2620:0:861:11b::/64")

    for device_name in devices:
        device = nb.dcim.devices.get(name=device_name)
        print(device)

        lo0 = nb.dcim.interfaces.create(device=device.id, name="lo0", type="virtual")
        print(f"  Created {lo0.name}")
        create_loop_ip(underlay_prefix, f"lo0.{device_name}.eqiad.wmnet", lo0)
        lo0_5000 = nb.dcim.interfaces.create(device=device.id, name="lo0.5000", type="virtual", vrf=2)
        print(f"  Created {lo0_5000.name}")
        create_loop_ip(overlay_prefix4, f"lo0-5000.{device_name}.eqiad.wmnet", lo0_5000)
        create_loop_ip(overlay_prefix6, f"lo0-5000.{device_name}.eqiad.wmnet", lo0_5000)
        print()

def create_loop_ip(pprefix, dns_name, nb_int):
    loop_ip = pprefix.available_ips.create()
    # Change netmask to /32 or /128 as it will have been created with parent prefix netmask
    if pprefix.family.value == 4:
        netmask=32
    else:
        netmask=128
    loop_ip.address=f"{ipaddress.ip_interface(loop_ip.address).ip}/{netmask}"
    loop_ip.dns_name=dns_name
    loop_ip.assigned_object_type="dcim.interface"
    loop_ip.assigned_object_id=nb_int.id
    loop_ip.save()
    print(f"    Assigned {loop_ip.address}.")

if __name__=="__main__":
    main()

