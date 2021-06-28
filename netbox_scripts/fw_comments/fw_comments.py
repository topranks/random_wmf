#!/usr/bin/python3

import argparse
import pynetbox
import ipaddress

parser = argparse.ArgumentParser(description='Stupid Netbox Thing')
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-f', '--file', help='File with firewall display set commands', type=str, required=True)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    current_term = ""
    with open(args.file) as f:
        for line in f.readlines():
            comment = ""
            if "term" in line:
                this_term = line.rstrip("\n").split()[7]
                if this_term != current_term:
                    current_term = this_term
                    print()
            if "from destination-address" in line or "from source-address" in line:
                addr = ipaddress.ip_network(line.rstrip("\n").split()[-1])
                # Single IP
                if addr.num_addresses == 1:
                    netbox_addr = nb.ipam.ip_addresses.get(address=str(addr.network_address))
                    if netbox_addr:
                        if netbox_addr.assigned_object_type == "dcim.interface":
                            interface = nb.dcim.interfaces.get(netbox_addr.assigned_object_id)
                            comment = "  # {} - {} ({})".format(interface.device, interface.name, netbox_addr.dns_name)
                        elif netbox_addr.assigned_object_type == "virtualization.vminterface":
                            interface = nb.virtualization.interfaces.get(netbox_addr.assigned_object_id)    
                            comment = "  # {} - {} ({})".format(interface.virtual_machine, interface.name, netbox_addr.dns_name)
                        else:
                            comment = "  # ({})".format(netbox_addr.dns_name)
                # Subnet
                else:
                    netbox_nets = nb.ipam.prefixes.filter(contains=addr.network_address)
                    if netbox_nets:
                        network = netbox_nets[-1]
                        comment = "  # {}".format(network.prefix)
                        if network.description:
                            comment += " - {}".format(network.description)
                        if network.site:
                            comment += " - {}".format(network.site)
                        if network.vlan:
                            vlan = nb.ipam.vlans.get(network.vlan.id)
                            comment += " - Vlan{} ({}/{}/{})".format(vlan.vid, vlan.name, vlan.group, vlan.description)

            print("{}{}".format(line.rstrip("\n"), comment))

if __name__=="__main__":
    main()

