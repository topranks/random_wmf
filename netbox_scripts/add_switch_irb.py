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

    eqiad_site = nb.dcim.sites.get(slug="eqiad")

    for vlan_id in range(1055,1061):
        vlan = nb.ipam.vlans.get(group_id=13, site_id=eqiad_site.id, vid=vlan_id)

        rack = vlan.name.split("-")[1]
        switch_name = f"lsw1-{rack}-eqiad"
        switch = nb.dcim.devices.get(name=switch_name)

        irb_int = nb.dcim.interfaces.create(device=switch.id,
                                            name=f"irb.{vlan_id}",
                                            description=vlan.name,
                                            vrf=2,
                                            type="virtual")
        print(f"{switch.name} - {irb_int.name}")

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)
        for prefix in prefixes:
            new_ip = prefix.available_ips.create()
            new_ip.assigned_object_type="dcim.interface"
            new_ip.assigned_object_id=irb_int.id
            new_ip.dns_name=f"irb-{vlan_id}.{switch_name}.eqiad.wmnet"
            new_ip.save()
            print(f"  {new_ip.address}")
        print()


if __name__=="__main__":
    main()

