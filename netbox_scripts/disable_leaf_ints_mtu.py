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

    devices = nb.dcim.devices.filter(name__isw='lsw1', site='codfw', status='planned')
    for device in devices:
        if device.name == "lsw1-d1-codfw":
            continue

        print(f"\n{device.name}")
        device_ints = nb.dcim.interfaces.filter(device_id=device.id, type__n='virtual')
        for device_int in device_ints:
            if device_int.connected_endpoint == None and device_int.name != "em0":
                device_int.enabled = False
                device_int.save()
                print(f"  Disabled {device_int.name}")
            elif device_int.name != "em0":
                device_int.mtu = 9192
                device_int.save()
                print(f"  Set mtu on {device_int.name}")

if __name__=="__main__":
    main()

