#!/usr/bin/python3

import yaml

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.factory.factory_loader import FactoryLoader

import json

import argparse
import sys
import os
import re
import pynetbox
from getpass import getpass
import ipaddress

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

interface_table:
  rpc: get-interface-information
  item: physical-interface
  view: interface_view

interface_view:
  fields:
    physical_interface: description

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
    global nb
    nb = pynetbox.api(nb_url, nb_key)

    globals().update(FactoryLoader().load(yaml.safe_load(junos_views_yaml)))

    nb_devices = nb.dcim.devices.filter(role='cr', status='active')
    for nb_device in nb_devices:
        problems = []
        dev_pri_ip = nb.ipam.ip_addresses.get(nb_device.primary_ip.id)
        junos_dev = get_junos_dev(dev_pri_ip.dns_name)

        # .to_json() seems to be the way to go but some of the other endpoints
        # (ospf etc) throw errors if you try it with them.  bug in pyez?
        int_data = json.loads(interface_table(junos_dev).get().to_json())
        int_descriptions = {int_name: int_desc['physical_interface'] for int_name, int_desc in int_data.items()}

        ospf_data = ospf_ints(junos_dev).get()
        for ospf_int in ospf_data:
            if ospf_int.int_type == "Down":
                phys_int = str(ospf_int.interface).split('.')[0]
                cct_url = get_int_cct_url(nb_device, phys_int)
                problems.append(f"{ospf_int.interface} Interface DOWN - {int_descriptions[phys_int]} - {cct_url}")
            elif ospf_int.int_type == "PtToPt" and int(ospf_int.neighbors) < 1:
                phys_int = str(ospf_int.interface).split('.')[0]
                cct_url = get_int_cct_url(nb_device, phys_int)
                problems.append(f"{ospf_int.interface} Interface DOWN - {int_descriptions[phys_int]} - {cct_url}")

        transit4_data = bgp_transit4(junos_dev).get()
        for bgp_peer in transit4_data:
            if bgp_peer.state != "Established":
                problems.append(get_bgp_error(nb_device, bgp_peer, int_descriptions))

        transit6_data = bgp_transit6(junos_dev).get()
        for bgp_peer in transit6_data:
            if bgp_peer.state != "Established":
                problems.append(get_bgp_error(nb_device, bgp_peer, int_descriptions))

        junos_dev.close()
        if problems:
            print(f"{nb_device.name:<10} FAILED")
            for problem in problems:
                print(f"    {problem}")
            print()
        else:
            print(f"{nb_device.name:<10} OK")


def get_bgp_error(nb_device, bgp_peer, int_descriptions):
    phys_int, cct_url = get_bgp_cct(nb_device, str(bgp_peer.address))
    if phys_int:
        try:
            return f"BGP to {bgp_peer.address} ASN {bgp_peer.asn} is DOWN - {phys_int} - {int_descriptions[phys_int]} - {cct_url}"
        except:
            print(phys_int)
            print(bgp_peer.address)
            pp(int_descriptions)
            print(f"\n{cct_url}")
    else:
        return f"BGP to {bgp_peer.address} ASN {bgp_peer.asn} is DOWN"


def get_int_cct_url(nb_device, int_name):
    nb_int = nb.dcim.interfaces.get(device_id=nb_device.id, name={int_name})
    if not nb_int or not nb_int.link_peers_type == 'circuits.circuittermination':
        return ''
    return nb_int.link_peers[0].circuit.url

def get_bgp_cct(nb_device, ip_addr):
    ip_obj = ipaddress.ip_address(ip_addr)
    if ip_obj.version == 4:
        pfxlen = 30
    else:
        pfxlen = 64
    ip_interface = ipaddress.ip_interface(f"{ip_addr}/{pfxlen}")
    nb_ip = nb.ipam.ip_addresses.get(parent=str(ip_interface.network), device_id=nb_device.id)
    if not nb_ip or not nb_ip.assigned_object_type =='dcim.interface':
        return '', ''
    nb_int = nb.dcim.interfaces.get(id=nb_ip.assigned_object.id)
    int_name = nb_int.name.split('.')[0]
    if not nb_int.link_peers_type == 'circuits.circuittermination':
        return int_name, ''
    return int_name, nb_int.link_peers[0].circuit.url

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
