#!/usr/bin/python3

import yaml

from jnpr.junos import Device
#from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError
from jnpr.junos.factory.factory_loader import FactoryLoader

import argparse
import sys
import os
import re

from pprintpp import pprint as pp
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--device', help='Device startswith', required=True, type=str)
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
parser.add_argument('-a', '--aspath', help='JunOS format as-path regex', required=True, type=str)
parser.add_argument('-p', '--prefix', help='Only output routes within prefix PFX', type=str, default='')
parser.add_argument('-t', '--table', help='Juniper table to query (default inet.0)', type=str, default='inet.0')
args = parser.parse_args()

# add extensive: True under args if needed

tableview_yaml = f'''
---
bgpRoutes:
  rpc: get-route-information
  args:
    protocol: bgp
    terse: True
    aspath-regex: {args.aspath}
    table: {args.table}
  item: route-table/rt
  key: rt-destination
  view: bgpView
 
bgpView:
  fields:
    prefix: rt-destination
    as_path: rt-entry/as-path
'''


#  rt_destination: rt-destination
#  rt_prefix_length: rt-prefix-length

def main():
    if args.prefix:
        prefix = ipaddress.ip_network(args.prefix)

    globals().update(FactoryLoader().load(yaml.safe_load(tableview_yaml)))

    junos_dev = get_junos_dev(args.device)
    return_data = bgpRoutes(junos_dev).get()
    junos_dev.close()

    routes = []
    max_characters = 0
    for route in return_data:
        if args.prefix:
            rt_prefix = ipaddress.ip_network(route.prefix)
            if not prefix.supernet_of(rt_prefix):
                continue
        if len(str(route.prefix)) > max_characters:
            max_characters = len(str(route.prefix))

        routes.append({
            route.prefix: set()
        })

        if type(route.as_path) == str:
            routes[-1][route.prefix].add(route.as_path)
        else:
            for path in route.as_path:
                routes[-1][route.prefix].add(path)
            
    space = " "
    for destination in routes:
        for route, paths in destination.items():
            path_num = 0
            for path in paths:
                if path_num == 0:
                    print(f"\n{route:<{(max_characters+1)}} {path}")
                    path_num += 1
                else:
                    print(f"{space:<{(max_characters+1)}} {path}")


def get_junos_dev(dev_name):
    # Initiates NETCONF session to router
    try:
        device = Device(dev_name, username=os.getlogin(), ssh_config=args.sshconfig, port=22)
        device.open()
    except ConnectError as err:
        print(f"Cannot connect to device: {err}")
        sys.exit(1)

    return device


if __name__ == '__main__':
    main()
