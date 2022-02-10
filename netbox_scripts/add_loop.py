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

    devices = ["lsw1-e1-eqiad", 
                "lsw1-e2-eqiad", 
                "lsw1-e3-eqiad", 
                "lsw1-e4-eqiad", 
                "lsw1-f1-eqiad", 
                "lsw1-f2-eqiad", 
                "lsw1-f3-eqiad", 
                "lsw1-f4-eqiad"]


    i=1 
    for device_name in devices:
        device = nb.dcim.devices.get(name=device_name)
        print(device)

        loop_int = nb.dcim.interfaces.create(device=device.id, name="lo0", type="virtual")
        print(loop_int)
        ip_addr = nb.ipam.ip_addresses.create(address=f"10.64.128.{i}/32",
                                                role="loopback",
                                                assigned_object_type="dcim.interface",
                                                assigned_object_id=loop_int.id)

        print(ip_addr)        


        i += 1


if __name__=="__main__":
    main()

