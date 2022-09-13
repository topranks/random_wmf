#!/usr/bin/python3

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

import argparse
import os

# Faidon peeringdb class
from peeringdb import PeeringDB

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message', help='Icinga Error Output', required=True, type=str)
parser.add_argument('-d', '--device', help='Device startswith', required=True, type=str)
parser.add_argument('-s', '--sshconfig', help='SSH config file', default='~/.ssh/config.homer')
args = parser.parse_args()

def main():
    print()
    as_numbers = {
        'inet': {},
        'inet6': {}
    }

    peering_db = PeeringDB(cachedir='/tmp/')

    # Parse ASNs and IP Version from Icinga message    
    for line in args.message.split("AS"):
        split_line = line.split(":")[0].split("/")
        try:
            asn = int(split_line[0])
        except ValueError:
            continue

        if asn < 64512 or (asn > 65535 and asn < 4200000000) or asn > 4294967294:
            ip_version = split_line[1]
            as_data = peering_db.fetch('asn', asn)[0]
            if split_line[1] == "IPv4":
                as_numbers['inet'][asn] = {}
                as_numbers['inet'][asn]['neighbors'] = set()
                as_numbers['inet'][asn]['config_max'] = 0
                as_numbers['inet'][asn]['info_max'] = as_data['info_prefixes4']
            else:
                as_numbers['inet6'][asn] = {}
                as_numbers['inet6'][asn]['neighbors'] = set()
                as_numbers['inet6'][asn]['config_max'] = 0
                as_numbers['inet6'][asn]['info_max'] = as_data['info_prefixes6']

    junos_dev = get_junos_dev(args.device)

    filter_xml = "<configuration><protocols><bgp/></protocols></configuration>"
    bgp_conf = junos_dev.rpc.get_config(options={'format':'json'}, filter_xml=filter_xml)

    for group in bgp_conf['configuration']['protocols']['bgp']['group']:
        if group['name'] == "IX4":
            inet_default = int(group['family']['inet']['unicast']['prefix-limit']['maximum'])
            for neighbor in group['neighbor']:
                if int(neighbor['peer-as']) in as_numbers['inet']:
                    as_numbers['inet'][int(neighbor['peer-as'])]['neighbors'].add(neighbor['name'])
                    try:
                        as_numbers['inet'][int(neighbor['peer-as'])]['config_max'] = \
                            neighbor['family']['inet']['unicast']['prefix-limit']['maximum']
                    except KeyError:
                        as_numbers['inet'][int(neighbor['peer-as'])]['config_max'] = inet_default
                    
        elif group['name'] == "IX6":
            inet6_default = int(group['family']['inet6']['unicast']['prefix-limit']['maximum'])
            for neighbor in group['neighbor']:
                if int(neighbor['peer-as']) in as_numbers['inet6']:
                    as_numbers['inet6'][int(neighbor['peer-as'])]['neighbors'].add(neighbor['name'])
                    try:
                        as_numbers['inet6'][int(neighbor['peer-as'])]['config_max'] = \
                            neighbor['family']['inet6']['unicast']['prefix-limit']['maximum']
                    except KeyError:
                        as_numbers['inet6'][int(neighbor['peer-as'])]['config_max'] = inet6_default
               
    clear_commands = [] 
    for ip_version, as_nums in as_numbers.items():
        if ip_version == "inet":
            group_name = "IX4"
        else:
            group_name = "IX6"
        for asn, as_conf in as_nums.items():
            if (as_conf['info_max'] * 1.1) > as_conf['config_max']:
                for neighbor_ip in as_conf['neighbors']:
                    print(f"set protocols bgp group {group_name} neighbor {neighbor_ip} family {ip_version} unicast prefix-limit maximum {int(as_conf['info_max'] * 1.2)}")
                    clear_commands.append(f"clear bgp neighbor {neighbor_ip}")
            else:
                for neighbor_ip in as_conf['neighbors']:
                    clear_commands.append(f"clear bgp neighbor {neighbor_ip}")

    print()
    for clear_command in clear_commands:
        print(clear_command)

    #print(junos_dev.cli("show version"))
    junos_dev.close()


def get_junos_dev(dev_name):
    # Initiates NETCONF session to router
    try:
        device = Device(dev_name, username=os.getlogin(), ssh_config=args.sshconfig, port=22)
        device.open()
    except ConnectError as err:
        print(f"Cannot connect to device: {err}")
        sys.exit(1)

    # Get config object
    device.bind(config=Config)

    return device


if __name__ == '__main__':
    main()
