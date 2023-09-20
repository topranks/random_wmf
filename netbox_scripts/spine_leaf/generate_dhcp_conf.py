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

    site_name = 'codfw'
#    install_server_name = 'install2004'

    site =  nb.dcim.sites.get(slug=site_name)
    vlan_group = nb.ipam.vlan_groups.get(slug='production', site=site.id)
#    install_server = nb.virtualization.virtual_machines.get(name=install_server_name)
#    install_server_ip = install_server.primary_ip4.address.split("/")[0]

    for vlan_id in range(2021, 2036):
        vlan = nb.ipam.vlans.get(group_id=vlan_group.id, vid=vlan_id)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)

        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            if type(pfx) == ipaddress.IPv4Network:
                print(f"# {vlan.name}")
                print(f"subnet {pfx.network_address} netmask {pfx.netmask} {{")
#                print("    authoritative;")
#                print("")
#                print(f"    option subnet-mask {pfx.netmask};")
                print(f"    option broadcast-address {pfx[-1]};")
                print(f"    option routers {pfx[1]};")
#                print(f"    option domain-name \"{site_name}.wmnet\";")
#                print("")
#                print(f"    next-server {install_server_ip}; # {install_server_name} (tftp server)")
                print("}")
                print("")




if __name__=="__main__":
    main()

