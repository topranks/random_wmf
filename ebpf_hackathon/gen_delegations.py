#!/usr/bin/python3 

import ipaddress
import yaml
from pathlib import Path

def main():
    with open('input_data.yaml', 'r') as input_file:
        input_data = yaml.safe_load(input_file.read())

    # Generate the A/AAAA name for each NS server IP passed
    dns_servers = []
    i=0
    for dns_ip in input_data['name_servers']:
        dns_servers.append({
            'hostname': f"ns{i}.{input_data['ns_zone']}.",
            'ip': ipaddress.ip_address(dns_ip)
        })
        i += 1

    # Create dicts to hold the zone delegations and cnames for each of the parent zones
    cnames = {}
    ptr_delegations = {}
    for parent_zone in input_data['parent_zones']:
        cnames[parent_zone] = []
        ptr_delegations[parent_zone] = []

    # Parse the CIDR networks and add the required zones and cnames to these dicts
    for cidr in input_data['cidrs']:
        net_addr = ipaddress.ip_network(cidr)
        if net_addr.version == 4:
            octets = 4 - int((net_addr.prefixlen - net_addr.prefixlen % 8) / 8)
            ptr_zone = '.'.join(net_addr[0].reverse_pointer.split('.')[octets:])
            parent_zone = get_parent_zone(ptr_zone, input_data['parent_zones'])
            if net_addr.prefixlen in (24, 16, 8):
                # We're at the dotted decimal boundry so can delegate the whole subnet
                ptr_delegations[parent_zone].append({
                    'subnet': net_addr,
                    'zone': ptr_zone.replace(f".{parent_zone}", "")
                })
            else:
                # We need to use RFC2317 format
                subnet_zone = f"{str(net_addr.network_address).split('.')[-1]}-{net_addr.prefixlen}"
                ptr_delegations[parent_zone].append({
                    'subnet': net_addr,
                    'zone': subnet_zone
                })
                i = 0
                while i < net_addr.num_addresses:
                    last_octet = i + int(str(net_addr.network_address).split(".")[-1])
                    cnames[parent_zone].append((last_octet, f"{last_octet}.{subnet_zone}.{ptr_zone}"))
                    i += 1

        elif net_addr.version == 6:
            ptr_zone = '.'.join(net_addr.network_address.reverse_pointer.split('.')[32-(net_addr.prefixlen//4):])
            parent_zone = get_parent_zone(ptr_zone, input_data['parent_zones'])
            ptr_delegations[parent_zone].append({
                'subnet': net_addr,
                'zone': ptr_zone.replace(f".{parent_zone}", "")
            })

    # write A/AAAA records for NS FWD entries
    Path("output").mkdir(exist_ok=True)
    with open(f"output/{input_data['ns_parent_zone']}", "w") as outfile:
        for dns_server in dns_servers:
            if dns_server['ip'].version == 4:
                outfile.write(f"{dns_server['hostname']:<31} IN    A      {dns_server['ip']}\n")
            else:
                outfile.write(f"{dns_server['hostname']:<31} IN    AAAA   {dns_server['ip']}\n")

    # write records for delegation inside each parent zone
    for parent_zone in input_data['parent_zones']:
        if len(ptr_delegations[parent_zone]) > 0:
            with open(f"output/{parent_zone}", "w") as outfile:
                for delegation in ptr_delegations[parent_zone]:
                    outfile.write(f"; Delegation for {delegation['subnet']}\n")
                    for dns_server in dns_servers:
                        outfile.write(f"{delegation['zone']:<31} IN    NS    {dns_server['hostname']}\n")
                outfile.write("\n")
                for cname_record in cnames[parent_zone]:
                    outfile.write(f"{cname_record[0]:<31} IN    CNAME {cname_record[1]}.\n")
                    

def get_parent_zone(ptr_zone, parent_zones):
    len_diff = 32
    correct_parent = ''
    for parent_zone in parent_zones:
        if parent_zone in ptr_zone:
            if (len(ptr_zone.split('.')) - len(parent_zone.split('.'))) < len_diff:
                correct_parent = parent_zone
                len_diff = len(ptr_zone.split('.')) - len(parent_zone.split('.'))

    return correct_parent
            

if __name__ == '__main__':
    main()
