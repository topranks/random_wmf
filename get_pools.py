#!/usr/bin/python3

import requests
import pynetbox

import json

from pprintpp import pprint as pp

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    pools_url = 'https://config-master.wikimedia.org/pools.json'

    resp = requests.get(pools_url)

    data = json.loads(resp.text)

    for cluster, devices in data['eqiad'].items():
        for fqdn, services in devices.items():
            device_name = fqdn.split(".")[0]
            nb_dev = nb.dcim.devices.get(name=device_name)
            if nb_dev:
                if nb_dev.rack.name.startswith("E") or nb_dev.rack.name.startswith("F"):
                    print(f"{nb_dev} - {nb_dev.rack} - {', '.join(services.keys())}")

if __name__=="__main__":
    main()



