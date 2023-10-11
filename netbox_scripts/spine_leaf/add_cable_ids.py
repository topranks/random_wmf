#!/usr/bin/python3

import argparse
import pynetbox
import sys
import pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    spines = {}
    spines['a1'] = {} 
    spines['a1']['device'] = nb.dcim.devices.get(name='ssw1-a1-codfw')
    spines['a1']['ints'] = list(nb.dcim.interfaces.filter(device_id=spines['a1']['device'].id))
    
    spines['a8'] = {}
    spines['a8']['device'] = nb.dcim.devices.get(name='ssw1-a8-codfw')
    spines['a8']['ints'] = list(nb.dcim.interfaces.filter(device_id=spines['a8']['device'].id))

    with open('cable_ids.txt', 'r') as cable_file:
        for line in cable_file.readlines():
            spine = spines[line.split("|")[1].lower()]['device']
            spine_ints = spines[line.split("|")[1].lower()]['ints']
            leaf_name = f"lsw1-{line.split('|')[2].lower()}-codfw"
            cable_id = int(line.split("|")[-1])

            for spine_int in spine_ints:
                if spine_int.connected_endpoint:
                    if spine_int.connected_endpoint.device.name == leaf_name:
                        cable = nb.dcim.cables.get(id=spine_int.connected_endpoint.cable)
                        cable.label = cable_id
                        cable.status = 'connected'
                        cable.save()

if __name__=="__main__":
    main()

