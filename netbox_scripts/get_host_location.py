#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open('/home/cmooney/homer5/config/sites.yaml', 'r') as stream:
        sites = yaml.safe_load(stream)

    hosts = set()
    for site_name, site_conf in sites.items():
        for key in site_conf.keys():
            if key in ('k8s_neighbors', 'k8s_stage_neighbors', 'k8s_mlserve_neighbors'):
                hosts.update(list(site_conf[key].keys()))

    for host in hosts:
        device = nb.dcim.devices.get(name=host)
        if device:
            interfaces = nb.dcim.interfaces.filter(device_id=device.id)
            for interface in interfaces:
                if interface.connected_endpoint:
                    print(f"{host:<20} wikimedia.org/node-location={interface.connected_endpoint.device.name}")

    for host in hosts:
        device = nb.virtualization.virtual_machines.get(name=host)
        if device:
            print(f"{host:<20} {device.cluster.name}")

    

if __name__=="__main__":
    main()

