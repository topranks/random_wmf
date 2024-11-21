#!/usr/bin/python3

import yaml

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.factory.factory_loader import FactoryLoader

import argparse
import sys
import os
import re
import pynetbox
from getpass import getpass

from pprintpp import pprint as pp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
args = parser.parse_args()

junos_views_yaml = '''
---
ospf_ints:
  rpc: get-ospf-interface-information
  args:
    brief: True
  item: ospf-interface
  view: ospf_int_view

ospf_int_view:
  fields:
    interface: interface-name
    neighbors: neighbor-count
    int_type: ospf-interface-state

bgp_transit4:
  rpc: get-bgp-summary-information
  args:
    group: "Transit4"
  item: bgp-peer
  view: bgp_transit_view

bgp_transit6:
  rpc: get-bgp-summary-information
  args:
    group: "Transit6"
  item: bgp-peer
  view: bgp_transit_view

bgp_transit_view:
  fields:
    address: peer-address
    asn: peer-as
    state: peer-state
'''

def main():
    nb_url = "https://{}".format(args.netbox)
    if args.key:
        nb_key = args.key
    else:
        nb_key = getpass(prompt="Netbox API Key: ")
    nb = pynetbox.api(nb_url, nb_key)

    globals().update(FactoryLoader().load(yaml.safe_load(junos_views_yaml)))

    nb_devices = nb.dcim.devices.filter(role='cr', status='active')
    for nb_device in nb_devices:
        problems = []
        dev_pri_ip = nb.ipam.ip_addresses.get(nb_device.primary_ip.id)
        junos_dev = get_junos_dev(dev_pri_ip.dns_name)

        ospf_data = ospf_ints(junos_dev).get()
        for ospf_int in ospf_data:
            if ospf_int.int_type == "Down":
                problems.append(f"{ospf_int.interface} Interface DOWN")
            if ospf_int.int_type == "PtToPt":
                if int(ospf_int.neighbors) < 1:
                    problems.append(f"{ospf_int.interface} OSPF DOWN")

        transit4_data = bgp_transit4(junos_dev).get()
        for bgp_peer in transit4_data:
            if bgp_peer.state != "Established":
                problems.append(f"BGP to {bgp_peer.address} ASN {bgp_peer.asn} is DOWN")

        transit6_data = bgp_transit6(junos_dev).get()
        for bgp_peer in transit6_data:
            if bgp_peer.state != "Established":
                problems.append(f"BGP to {bgp_peer.address} ASN {bgp_peer.asn} is DOWN")

        junos_dev.close()
        if problems:
            print(f"{nb_device.name:<10} FAILED")
            for problem in problems:
                print(f"    {problem}")
            print()
        else:
            print(f"{nb_device.name:<10} OK")


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
