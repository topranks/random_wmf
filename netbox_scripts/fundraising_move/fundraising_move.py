#!/usr/bin/python3

import pynetbox
import argparse
from pathlib import Path
from getpass import getpass
from requests import Session
import sys

from pprintpp import pprint as pp

parser = argparse.ArgumentParser(description='Frack server move script')
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='Netbox API Token / Key', type=str, default='')
args=parser.parse_args()

USER_AGENT = "Frack move script cathal"
SITE="eqiad"
SOURCE_RACK = "C1"
DEST_RACKS = ["E15", "E16"]
VLAN_LOCATIONS = { "frack-fundraising1-c-eqiad": "E16" }

def main():
    """Updates location to rack E15 or E16 based on current rack height and attached vlan"""
    print("Getting data... ", end="", flush=True)
    nb = get_nb(ua=USER_AGENT)
    source_rack = nb.dcim.racks.get(name=SOURCE_RACK, site=SITE)
    gql_query = Path('server_vlans.gql').read_text()
    gql_vars = {'rack_id': [str(source_rack.id)]}
    nb_data = get_graphql_query(nb, gql_query, gql_vars, USER_AGENT)

    new_racks = {rack: nb.dcim.racks.get(name=rack, site=SITE) for rack in DEST_RACKS}
    new_switches = {}
    for rack in DEST_RACKS[1:]:
        for sw_num in ("a", "b"):
            switch_name = f"fasw2-{rack.lower()}{sw_num}-{SITE}"
            new_switches[switch_name] = nb.dcim.devices.get(name=switch_name)

    print()
    fake_label = 0
    for server in nb_data['device_list']:
        vlan = server['interfaces'][0]['connected_endpoints'][0]['untagged_vlan']
        vlan_name = vlan['name']
        # We assume the first rack in DEST_RACKS is default if the vlan doesn't point to another
        new_rack_name = VLAN_LOCATIONS[vlan_name] if vlan_name in VLAN_LOCATIONS else DEST_RACKS[0]
        print(f"{server['name']} is in vlan {vlan_name} - moving to rack {new_rack_name}... ", end="", flush=True)
        nb_server = nb.dcim.devices.get(id=server['id'])
        nb_server.rack = new_racks[new_rack_name].id
        nb_server.location = new_racks[new_rack_name].location.id
        nb_server.save()
        print("done.")

        if new_rack_name != DEST_RACKS[0]:
            for interface in server['interfaces']:
                sw_port = interface['connected_endpoints'][0]
                old_cable = nb.dcim.cables.get(id=interface['cable']['id'])
                link_ab = interface['name'].replace("PRIMARY_", "").lower()
                new_switch_name = f"fasw2-{new_rack_name.lower()}{link_ab}-{SITE}"
                print(f"Creating new interface {sw_port['name']} on {new_switch_name}... ", end='', flush=True)
                new_switch_int = nb.dcim.interfaces.create(device=new_switches[new_switch_name].id, name=sw_port['name'],
                    untagged_vlan=vlan['id'], mode="access", mtu=9212, type=interface['type'])
                new_switch_int.save()
                print("done.")
                print(f"Deleting old cable from {server['name']} {interface['name']} to {sw_port['device']['name']} {sw_port['name']}... ", end='', flush=True)
                old_cable.delete()
                print("done.")
                print(f"Deleting old interface {sw_port['name']} on {sw_port['device']['name']}... ", end='', flush=True)
                old_nb_switch_int = nb.dcim.interfaces.get(id=sw_port['id'])
                old_nb_switch_int.delete()
                print("done.")
                print(f"Creating new cable from {server['name']} {interface['name']} to {new_switch_name} {sw_port['name']}... ", end='', flush=True)
                new_cable_label = interface['cable']['label'] if interface['cable']['label'] else f"changeme_{new_switch_name}_{fake_label}"
                new_cable = nb.dcim.cables.create(
                    a_terminations = [{'object_type': 'dcim.interface', 'object_id': new_switch_int.id}],
                    b_terminations = [{'object_type': 'dcim.interface', 'object_id': interface['id']}],
                    label=new_cable_label, color=interface['cable']['color'])
                new_cable.save()
                print("done.")
                fake_label += 1
        print()


def get_graphql_query(nb: pynetbox.core.api.Api, query: str, variables: dict = None, agent: str = "test script") -> dict:
    """Sends graphql query to netbox and returns JSON result as dict"""
    nb_key = args.key if args.key else getpass(prompt="Netbox API token: ")
    data = {"query": query}
    if variables is not None:
        data['variables'] = variables

    response = nb.http_session.post(url=nb.base_url.replace('/api', '/graphql/'), json=data)
    response.raise_for_status()
    if not response.json()['data']:
        print(f"ERROR: {response.text}")
        sys.exit(1)
    return response.json()['data']


def get_nb(ua: str = "netops script"):
    nb_url = "https://{}".format(args.netbox)
    nb_key = args.key if args.key else getpass(prompt="Netbox API token: ")
    nb = pynetbox.api(nb_url, token=nb_key)
    http_session = Session()
    http_session.headers.update({'User-Agent': ua})
    http_session.headers.update({'Authorization': f'Token {nb_key}'})
    nb.http_session = http_session
    return nb


if __name__=="__main__":
    main()

