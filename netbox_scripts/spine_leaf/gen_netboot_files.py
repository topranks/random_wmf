#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress
import shutil
import os

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-d', '--directory', help='Output directory', type=str, default="netboot")
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    if os.path.isdir(args.directory):
        print(f"Deleting directory \"{args.directory}\"...", end='')
        shutil.rmtree(args.directory)
        print(" done.\n")

    os.mkdir(args.directory)

    with open(f"{args.directory}/netboot.cfg_additions", "w") as nbconf:
        for vlan_id in range(2021, 2036):
            vlan = nb.ipam.vlans.get(vid=vlan_id)
            print(vlan.name)

            v4_pfx_nb = nb.ipam.prefixes.get(vlan_id=vlan.id, family=4)
            v4_pfx = ipaddress.ip_network(v4_pfx_nb.prefix)
            site = vlan.name.split("-")[-1]

            nbconf.write(f"        {v4_pfx[1]}) echo subnets/{vlan.name}.cfg ;; \\\n")

            with open(f"{args.directory}/{vlan.name}.cfg", "w") as nbfile:
                nbfile.write("# SPDX-License-Identifier: Apache-2.0\n")
                nbfile.write("# subnet specific configuration settings\n\n")
                nbfile.write("# get_domain should be set, get_hostname is overwritten by DHCP\n")
                if v4_pfx.is_private:
                    nbfile.write(f"d-i	netcfg/get_domain	string	{site}.wmnet\n\n")
                else:
                    nbfile.write(f"d-i   netcfg/get_domain   string  wikimedia.org\n\n")
                nbfile.write("# ip address is taken from DHCP, rest is set here\n")
                nbfile.write(f"d-i	netcfg/get_netmask	string	{v4_pfx.netmask}\n")
                nbfile.write(f"d-i	netcfg/get_gateway	string	{v4_pfx[1]}\n")
                nbfile.write("d-i	netcfg/confirm_static	boolean	true\n\n")

                if v4_pfx.is_private:
                    nbfile.write(f"d-i	mirror/http/proxy	string	http://webproxy.{site}.wmnet:8080\n")

if __name__=="__main__":
    main()

