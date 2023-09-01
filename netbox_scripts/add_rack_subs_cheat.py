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

    with open('rack_vlans.txt', 'r') as vlan_file:
        vlan_lines = vlan_file.readlines()

    for line in vlan_lines:
        splitline = line.rstrip().split()
        rack = splitline[0].lower()
        rack_vlans = {"private1": {}, "analytics1": {}}
        rack_vlans['private1']['vlan_id'] = int(splitline[1])
        rack_vlans['analytics1']['vlan_id'] = int(splitline[2])
        rack_vlans['private1']['subnet4'] = splitline[3]
        rack_vlans['analytics1']['subnet4'] = splitline[4]
        rack_vlans['private1']['subnet6'] = splitline[5]
        rack_vlans['analytics1']['subnet6'] = splitline[6]

       #  print(f"{rack} - {rack_vlans}")
        for vlan_type in ["private1", "analytics1"]:
            vlan_name = f"{vlan_type}-{rack}-eqiad"
            print(f"{rack_vlans[vlan_type]['vlan_id']} - {vlan_name} - {rack_vlans[vlan_type]['subnet4']} - {rack_vlans[vlan_type]['subnet6']}")

            '''
            new_vlan = nb.ipam.vlans.create(site=eqiad_site.id,
                                    vid=rack_vlans[vlan_type]['vlan_id'],
                                    name=vlan_name,
                                    group=13)

            v4_subnet = nb.ipam.prefixes.create(prefix=rack_vlans[vlan_type]['subnet4'],
                                                site=eqiad_site.id,
                                                vlan=new_vlan.id,
                                                description = vlan_name)

            v6_subnet = nb.ipam.prefixes.create(prefix=rack_vlans[vlan_type]['subnet6'],
                                                site=eqiad_site.id,
                                                vlan=new_vlan.id,
                                                description = vlan_name)
            '''


if __name__=="__main__":
    main()

