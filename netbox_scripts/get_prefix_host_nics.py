#!/usr/bin/python3

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

    ips = nb.ipam.ip_addresses.filter(parent=args.prefix)

    for ip in ips:
        interface = ip.assigned_object
        device = nb.dcim.devices.get(interface.device.id)

        if device.device_type.display_name.lower().startswith("dell"):
            device_ints = nb.dcim.interfaces.filter(device_id=device.id)
            for device_int in device_ints:
                try:
                    device_cable = nb.dcim.cables.get(device_int.connected_endpoint.cable)
                except AttributeError:
                    continue

                if device_cable.termination_a.device.name == device.name:
                    print(f"{device.name} - {device_int.name}: {device_cable.termination_b.device.name}")
                else:
                    print(f"{device.name} - {device_int.name}: {device_cable.termination_a.device.name}")

        print("")



if __name__=="__main__":
    main()

