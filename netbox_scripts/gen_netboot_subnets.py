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

    i = 0
    while i<16:
        vlan_id = 1031 + i
        i += 1

        vlan = nb.ipam.vlans.get(group_id=13, vid=vlan_id)

        prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)


        outfile = open(f"{vlan.name}.cfg", 'w')

        for prefix in prefixes:
            pfx = ipaddress.ip_network(prefix)
            if type(pfx) == ipaddress.IPv4Network:
                outfile.write(f"# subnet specific configuration settings\n")
                outfile.write(f"\n")
                outfile.write(f"# get_domain should be set, get_hostname is overwritten by DHCP\n")
                outfile.write(f"d-i	netcfg/get_domain	string	eqiad.wmnet\n")
                outfile.write(f"\n")
                outfile.write(f"# ip address is taken from DHCP, rest is set here\n")
                outfile.write(f"d-i	netcfg/get_netmask	string	{pfx.netmask}\n")
                outfile.write(f"d-i	netcfg/get_gateway	string	{pfx[1]}\n")
                outfile.write(f"d-i	netcfg/confirm_static	boolean	true\n")
                outfile.write(f"\n")
                outfile.write(f"d-i	mirror/http/proxy	string	http://webproxy.eqiad.wmnet:8080")
                outfile.write(f"\n")
                outfile.write(f"# NTP\n")
                outfile.write(f"d-i	clock-setup/ntp-server	string	ntp.eqiad.wikimedia.org\n")

                print(f"{pfx[1]}) echo subnets/{vlan.name}.cfg ;; \\")

        outfile.close()


if __name__=="__main__":
    main()

