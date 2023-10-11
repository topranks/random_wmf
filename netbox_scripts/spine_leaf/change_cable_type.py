#!/usr/bin/python3
import argparse
import pynetbox
import sys
import ipaddress
import yaml
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)


    for device_name in ['ssw1-a1-codfw', 'ssw1-a8-codfw']:
        device = nb.dcim.devices.get(name=device_name)
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)
        for interface in interfaces:
            if interface.connected_endpoint:
                cable = nb.dcim.cables.get(id=interface.connected_endpoint.cable)
                cable.type = "mmf"
                cable.color = "ff66ff"
                cable.save()
                print(f"{cable.termination_a.device} - {cable.termination_b.device} - {cable.type} - {cable.color}")



if __name__=="__main__":
    main()

