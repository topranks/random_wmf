#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-d', '--device', help='Device (asw etc) to poll for', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

#    device = nb.dcim.devices.get(name=args.device)

    interfaces = nb.dcim.interfaces.filter(device=args.device)

    for interface in interfaces:
        try:
            cable = nb.dcim.cables.get(interface.connected_endpoint.cable)
        except AttributeError:
            continue

        if cable.termination_a.device.name == args.device:
            device = nb.dcim.devices.get(cable.termination_b.device.id)
        else:
            device = nb.dcim.devices.get(cable.termination_a.device.id)

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

