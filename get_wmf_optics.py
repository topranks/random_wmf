#!/usr/bin/python3

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError

import xmltodict
from lxml import etree

import os
import argparse

#import logging
#logging.basicConfig(level=logging.DEBUG)

import requests
import json
import sys

import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='/home/cmooney/.ssh/config.homer')
parser.add_argument('--sshkey', help='SSH key to use file', default='/home/cmooney/.ssh/id_ed25519')
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
args = parser.parse_args()

def main():
    """Gets the active number of each type of SFP module in use at all of our sites"""
    routers = get_router_fqdns()
    optics = {}
    for router, site in routers.items():
        print(f"{router}... ", end='', flush=True)
        # Add site to dict
        if site not in optics:
            optics[site] = {}
        global junos_dev
        junos_dev = get_junos_dev(router)
        # Get list of interfaces so we can determine which are enabled, we don't count not-enabled as they 
        # might be spares in the slot but unconfigured (so should count as spares not active in use
        enabled_ints = get_enabled_ints()

        fpc_info = parse_rpc_result(junos_dev.rpc.get_pic_information())
        # SRX1600 hive brain scenario
        if "multi-routing-engine-results" in fpc_info:
            fpc_list = []
            for node_fpc in fpc_info['multi-routing-engine-results']['multi-routing-engine-item']:
                fpc_list.append(node_fpc['fpc-information']['fpc'])
            # We hard-code the FPC from the second (last) node of the cluster as 7 to match the int naming
            fpc_list[-1]['slot'] = "7"
        else:
            fpc_list = fpc_info['fpc-information']['fpc'] if type(fpc_info['fpc-information']['fpc']) == list else [fpc_info['fpc-information']['fpc']]

        for fpc in fpc_list:
            if fpc['state'] != "Online":
                continue
            fpc_slot = fpc['slot']
            pic_list = fpc['pic'] if type(fpc['pic']) == list else [fpc['pic']]
            for pic in pic_list:
                if pic['pic-state'] != "Online":
                    continue
                pic_slot = pic['pic-slot']
                pic_info = parse_rpc_result(junos_dev.rpc.get_pic_detail(fpc_slot=fpc_slot, pic_slot=pic_slot))
                if "multi-routing-engine-results" in pic_info:  # SRX Hive mind, but it only has one set of results here
                    pic_detail = pic_info['multi-routing-engine-results']['multi-routing-engine-item']['fpc-information']['fpc']['pic-detail']
                else:
                    pic_detail = pic_info['fpc-information']['fpc']['pic-detail']
                if "port-information" not in pic_detail or pic_detail['port-information'] is None:
                    # Non-modular pics (i.e. 48xGE built-in), or ones with no modules installed (empty port-information)
                    continue
                ports = pic_detail['port-information']['port'] if type(pic_detail['port-information']['port']) == list else [pic_detail['port-information']['port']]
                for port_info in ports:
                    int_ref = f"{fpc_slot}/{pic_slot}/{port_info['port-number']}"
                    if int_ref not in enabled_ints:
                        continue
                    sfp_type = get_sfp_type(port_info)
                    if sfp_type not in optics[site]:
                        optics[site][sfp_type] = 0
                    optics[site][sfp_type] += 1
        junos_dev.close()
        print("done.")

    print_results(optics)


def print_results(optics):
    """Prints the results as YAML and sorts by number of each module."""
    print()
    sorted_data = {}
    for site, transceivers in optics.items():
        sorted_modules = dict(sorted(transceivers.items(), key=lambda item: item[1], reverse=True))
        print(yaml.dump({site: sorted_modules}))
        print()


def get_sfp_type(port_info):
    """Returns a single string representing the SFP type based on port-info, can be as simple as the 
       cable-type (i.e. 10GBase-LR) but we may need to set up aliases or use more of the info depending 
       on if we have odd names coming back for some SFPs which are really the same type"""

    return port_info['cable-type']

                
def get_enabled_ints():
    """Returns the enabled interfaces we care about"""
    interface_info = parse_rpc_result(junos_dev.rpc.get_interface_information(media=True, terse=True))

    enabled_ints = []
    for interface in interface_info['interface-information']['physical-interface']:
        if not interface['name'].startswith(('ge', 'xe', 'et')) or interface['admin-status'] == "down":
            continue
        enabled_ints.append(interface['name'].split("-")[1])

    return enabled_ints


def parse_rpc_result(xml):
    xml_str = etree.tostring(xml)
    return xmltodict.parse(xml_str)


def get_router_fqdns() -> list:
    """Gets list of IPs in Netbox with dns_name attributes"""
    device_query = """
        {
          device_list(filters: {status:"active", manufacturer:"juniper"}) {
            name
            primary_ip4 {
              dns_name
            }
            site { slug }
          }
        }
    """
    result = get_graphql_query(device_query)['device_list']
    return {router['primary_ip4']['dns_name']: router['site']['slug'] for router in result if router['primary_ip4']}


def get_graphql_query(query: str) -> dict:
    """Sends graphql query to netbox and returns JSON result as dict"""
    url = f"https://{args.netbox}/graphql/"
    headers = {
        'Authorization': f'Token {args.key}'
    }
    data = {"query": query}
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


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
