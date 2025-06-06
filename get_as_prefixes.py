#!/usr/bin/python3

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError

import xmltodict
from lxml import etree

import os
import argparse
import ipaddress

#import logging
#logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='/home/cmooney/.ssh/config.homer')
parser.add_argument('--sshkey', help='SSH key to use file', default='/home/cmooney/.ssh/id_ed25519')
parser.add_argument('-r', '--router', help='Hostname of router to get table from', required=True, type=str)
parser.add_argument('-a', '--aspath', help='Juniper regular expression for BGP paths', required=True, type=str)
args = parser.parse_args()

def main():
    junos_dev = get_junos_dev(args.router)

    # The 'get_route_information' is basically 'show route', we can find this by running 
    # the CLI command with "| display xml rpc"
    xml = junos_dev.rpc.get_route_information(terse=True, protocol='bgp', aspath_regex=args.aspath, dev_timeout=120)
    xml_str = etree.tostring(xml)
    data = xmltodict.parse(xml_str)

    route_tables = {}

    for route_table in data['route-information']['route-table']:
        if 'rt' not in route_table:
            continue
        table_name = route_table['table-name']
        route_tables[table_name] = []
        for route in route_table['rt']:
            route_obj = ipaddress.ip_network(route['rt-destination'])
            route_tables[table_name].append(route_obj)

    print("FULL ROUTES:\n")
    for table_name, routes in route_tables.items():
        print(f"Table: {table_name}")
        for route in routes:
            print(f"    {route}")
        print()

    print("****************************************")
    print("AGGREGATED ROUTES:\n")
    for table_name, routes in route_tables.items():
        print(f"Table: {table_name}")
        for route in list(ipaddress.collapse_addresses(routes)):
            print(f"    {route}")
        print()


def get_junos_dev(dev_name):
    # Initiates NETCONF session to router
    try:
        device = Device(dev_name, username=os.getlogin(), ssh_config=args.sshconfig, port=22)
        device.open()
    except ConnectError as err:
        print(f"Cannot connect to device: {err}")
        print(err.with_traceback())
        sys.exit(1)

    return device


if __name__ == '__main__':
    main()
