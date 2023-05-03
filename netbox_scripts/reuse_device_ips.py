#!/usr/bin/python3

import argparse
import pynetbox
import json

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    int_details = {}

    device = nb.dcim.devices.get(name='lvs2007')
    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for interface in interfaces:
        int_details[interface.name] = {}
        ips = nb.ipam.ip_addresses.filter(interface_id=interface.id)
        if interface.connected_endpoint:
            int_details['connection'] = {}
            int_details['connection']['device'] = interface.connected_endpoint.device.name
            int_details['connection']['interface'] = interface.connected_endpoint.name
        ips = nb.ipam.ip_addresses.filter(interface_id=interface.id)
        if ips:
            int_details[interface.name]['ips'] = []
            for ip in ips:
                int_details[interface.name]['ips'].append({ str(ip): ip.dns_name })

    print(json.dumps(int_details, indent=2))

if __name__=="__main__":
    main()

