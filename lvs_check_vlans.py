#!/usr/bin/python3

import ipaddress
import subprocess
import json
import argparse



def main():
    parser = argparse.ArgumentParser(description='Checks LVS sub-interface reachability to GW')
    parser.add_argument('-d', '--device', help='IP or hostname of device.', required=True)
    args=parser.parse_args()

    raw_output = subprocess.getoutput(f"ssh {args.device} ip --json addr show")
    ip_info = json.loads(raw_output)

    for interface in ip_info:
        if not interface['ifname'].startswith("vlan"):
            continue
        print(f"# {interface['ifname']}")
        for addr_data in interface['addr_info']:
            if addr_data['scope'] == "link":
                continue
            address = ipaddress.ip_interface(f"{addr_data['local']}/{addr_data['prefixlen']}")
            print(f"ping -c 2 {address.network[1]}")
        print()


if __name__ == "__main__":
    main()

