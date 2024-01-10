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

    devices = nb.dcim.devices.filter(device_type_id=[163, 201, 151], site='eqiad')
    for device in devices:
        print(f"{device.name} - {device.device_type.model}")
        print(type(device.device_type.model))
        break


        '''
        interfaces = nb.dcim.interfaces.filter(device_id=device.id, name__isw="em", mgmt_only=True)
        if not interfaces:
            print(f"{device.name}.. ", end='')
            em0 = nb.dcim.interfaces.create(name='em0', device=device.id, type='1000base-t', mgmt_only=True, enabled=True)
            em0.save()
            em1 = nb.dcim.interfaces.create(name='em1', device=device.id, type='1000base-t', mgmt_only=True, enabled=True)
            em1.enabled = False
            em1.save()
            print("done.")
        '''



if __name__=="__main__":
    main()

