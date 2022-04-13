#!/usr/bin/python3

import pysnooper

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-p', '--prefix', help='Prefix to pull devices from', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    # Get prefix or aggregate from Netbox for supplied network and initiate 'subnets' dict with it
    nb_pfx = nb.ipam.prefixes.get(prefix=args.prefix)
    pfx_desc = ""
    if nb_pfx:
        pfx_desc = nb_pfx.description
    else:
        nb_agg = nb.ipam.aggregates.get(prefix=args.prefix)
        if nb_agg:
            pfx_desc = nb_agg.description

    subnets = {
        ipaddress.ip_network(args.prefix): {
            "ips": [],
            "desc": pfx_desc
        }
    }

    # Get child prefixes of supplied aggregate
    child_pfx = nb.ipam.prefixes.filter(within=args.prefix)
    for pfx in child_pfx:
        pfx_desc = ""
        if pfx.description:
            pfx_desc = pfx.description
        elif pfx.vlan:
            pfx_desc = f"Vlan {pfx.vlan.vid} ({pfx.vlan.name})"
        elif pfx.role:
            pfx_desc = pfx.role.name

        subnets[ipaddress.ip_network(pfx.prefix)] = {
            "ips": [],
            "desc": pfx_desc
        }


    # Get IPs that are within supplied agg prefix, work out which is smallest subnet they fit into
    ips = nb.ipam.ip_addresses.filter(parent=args.prefix)
    for ip in ips:
        ip_addr = ipaddress.ip_interface(ip)
        host_net = ipaddress.ip_network(f"{ip_addr.ip}/32")
        current_best = ipaddress.ip_network(args.prefix)
        for pfx in subnets.keys():
            if pfx == host_net:
                subnets[pfx]['ips'].append(ip)
                break
            elif pfx.supernet_of(host_net) and pfx.prefixlen > current_best.prefixlen:
                current_best = pfx

        subnets[current_best]['ips'].append(ip)

           
    for prefix, details in subnets.items():
        pfx_str = f"{str(prefix):<27}"
        if details['desc']:
            pfx_str += f"{details['desc']}"
        print(pfx_str)
        for ip in details['ips']:
            if ip.assigned_object:
                device = None
                try:
                    device = ip.assigned_object.device.display_name
                except AttributeError:
                    try:
                        device = ip.assigned_object.virtual_machine.name
                    except:
                        pass
                print(f"    {str(ip):<22} {device + ':' + ip.assigned_object.name:<30} {ip.dns_name}")
            else:
                print(f"    {str(ip):<22} {ip.description:<30} {ip.dns_name}")
        print("")


if __name__=="__main__":
    main()

