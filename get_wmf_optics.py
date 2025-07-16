#!/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor, as_completed

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError

import xmltodict
from lxml import etree

import os
import argparse

#import logging
#logging.basicConfig(level=logging.DEBUG)

import requests
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

    tasks = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        for router, site in routers.items():
            tasks.append(executor.submit(get_router_sfp_count, router, site))

        for task in as_completed(tasks):
            sfps, site = task.result()
            if site not in optics:
                optics[site] = {}
            for sfp_type, count in sfps.items():
                if sfp_type not in optics[site]:
                    optics[site][sfp_type] = 0
                optics[site][sfp_type] += count

    print_results(optics)

def get_router_sfp_count(router, site):
    """Gets the number of optics of each type for a given router"""
    optics = {}
    junos_dev = get_junos_dev(router)
    print(f"Connected to {router}.")

    # Get list of enabled interfaces, we won't count SFPs in disabled ports as used.
    enabled_ints = get_enabled_ints(junos_dev)
    # Get FPC & PIC info from device
    fpc_info = parse_rpc_result(junos_dev.rpc.get_pic_information())
    if "multi-routing-engine-results" in fpc_info:
        # SRX multi-node cluster will return the list of FPCs for each physical device
        fpc_list = []
        for node_fpc in fpc_info['multi-routing-engine-results']['multi-routing-engine-item']:
            fpc_list.append(node_fpc['fpc-information']['fpc'])
        # We hard-code the FPC from the second (last) node of the cluster as 7 to match the int naming
        fpc_list[-1]['slot'] = "7"
    else:
        fpc_list = fpc_info['fpc-information']['fpc']

    # Loop over each FPC and ask for the SFPs for each PIC
    for fpc in fpc_list if isinstance(fpc_list, list) else [fpc_list]:
        if fpc['state'] != "Online":
            continue
        for pic in fpc['pic'] if isinstance(fpc['pic'], list) else [fpc['pic']]:
            if pic['pic-state'] != "Online":
                continue
            pic_info = parse_rpc_result(junos_dev.rpc.get_pic_detail(fpc_slot=fpc['slot'], pic_slot=pic['pic-slot']))
            if "multi-routing-engine-results" in pic_info:  
                # SRX hive mind again, but it only has one set of results here
                pic_detail = pic_info['multi-routing-engine-results']['multi-routing-engine-item']['fpc-information']['fpc']['pic-detail']
            else:
                pic_detail = pic_info['fpc-information']['fpc']['pic-detail']
            if "port-information" not in pic_detail or pic_detail['port-information'] is None:
                # Non-modular pics (i.e. 48xGE built-in), or ones with no modules installed (empty port-information)
                continue
            ports = pic_detail['port-information']['port'] 
            for port_info in ports if isinstance(ports, list) else [ports]:
                interface_number = f"{fpc['slot']}/{pic['pic-slot']}/{port_info['port-number']}"
                if interface_number not in enabled_ints:
                    continue
                sfp_type = get_sfp_type(port_info)
                if sfp_type not in optics:
                    optics[sfp_type] = 0
                optics[sfp_type] += 1

    junos_dev.close()
    return optics, site


def print_results(optics):
    """Prints the results as YAML and sorts by number of each module."""
    print()
    sorted_modules = {}
    # Sort the list of sites by which has the most overall SFPs
    sorted_sites = dict(sorted(optics.items(), key=lambda item: sum(item[1].values()), reverse=True))
    # Now sort the modules at each site and print them out
    for site, modules in sorted_sites.items():
        sorted_modules = dict(sorted(modules.items(), key=lambda item: item[1], reverse=True))
        print(yaml.dump({site: sorted_modules}, sort_keys=False))


def get_sfp_type(port_info):
    """Managles the SFP names as we need to to make the output cleaner"""
    sfp_type = port_info['cable-type'].replace("BASE ", "-")
    alias = {
        "100G-LR4 Lite": "100G-CWDM4",
        "GIGE 1000LX10": "1G-LX",
        "4X10G-LR": "4x10G-LR"
    }
    sfp_type = alias[sfp_type] if sfp_type in alias else sfp_type

    use_code_for = ('unknown')
    if sfp_type.lower().startswith((use_code_for)):
        sfp_type = port_info['sfp-vendor-pno']

    return sfp_type


                
def get_enabled_ints(junos_dev):
    """Returns the enabled interfaces we care about"""
    interface_info = parse_rpc_result(junos_dev.rpc.get_interface_information(media=True, terse=True))
    enabled_ints = []
    for interface in interface_info['interface-information']['physical-interface']:
        if not interface['name'].startswith(('ge', 'xe', 'et')) or interface['admin-status'] == "down":
            continue
        enabled_ints.append(interface['name'].split("-")[1].split(":")[0])

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
