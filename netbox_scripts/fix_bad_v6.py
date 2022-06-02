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

    ipv6_parent = "2620:0:861:fe00::/55"
    pprefix = nb.ipam.prefixes.get(prefix=ipv6_parent)

    eqiad_site = nb.dcim.sites.get(slug="eqiad")


    vlans = [1109, 1110, 1111, 1125, 1126]

    for vlan_id in vlans:
        vlan = nb.ipam.vlans.get(site_id=eqiad_site.id, vid=vlan_id)

        old_pfx = nb.ipam.prefixes.get(vlan_id=vlan.id, family=6)
        old_ips = nb.ipam.ip_addresses.filter(parent=str(old_pfx))

        new_pfx = pprefix.available_prefixes.create({"prefix_length": 64})
        new_pfx.site = eqiad_site.id
        new_pfx.vlan = vlan.id
        new_pfx.save()

        new_pfx_obj = ipaddress.ip_network(str(new_pfx))
        
        print(f"{old_pfx}  TO  {new_pfx_obj}")

        for ip_obj in old_ips:
            ip_addr = ipaddress.ip_interface(ip_obj.address)
            ip_index = int(ip_addr.ip) - int(ip_addr.network.network_address)

            new_ip = ipaddress.ip_interface(f'{new_pfx_obj[ip_index]}/{new_pfx_obj.prefixlen}')

            new_nb_ip = nb.ipam.ip_addresses.create(address=str(new_ip),
                                                    assigned_object_type="dcim.interface",
                                                    assigned_object_id=ip_obj.assigned_object_id,
                                                    dns_name=ip_obj.dns_name)

            ip_obj.delete()

            print(f"    {ip_addr} - {new_ip} - {ip_obj.assigned_object} - {ip_obj.dns_name}")        

        old_pfx.delete()
        print("")


if __name__=="__main__":
    main()

