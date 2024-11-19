#!/usr/bin/python3

import argparse
from getpass import getpass
import pynetbox
import sys
import ipaddress
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', type=str, default='')
parser.add_argument('--host', help='Host to check', required=True, type=str)
parser.add_argument('--verbose', help='Also print the generated config', default=False)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    if args.key:
        nb_key = args.key
    else:
        nb_key = getpass(prompt="Netbox API token: ")
    global nb
    nb = pynetbox.api(nb_url, token=nb_key)

    nb_changes = False
    host = nb.dcim.devices.get(name=args.host)
    physical_int, switch, switch_int = get_switch_int(host)

    if not str(physical_int).startswith('e'):
        # Proper netdev name hasn't yet been imported from puppet to Netbox
        physical_int = "<primary_int>"

    # Get the private vlan host has been provisioned for
    private_vlan = nb.ipam.vlans.get(name=switch_int.untagged_vlan.name)
    private_vlan_location = private_vlan.name.split('-')[1]
    if host.site.slug in ('codfw', 'eqiad') and len(private_vlan_location) > 1:
        print(f"{host} is configured on rack-specific vlan {private_vlan} instead of row-wide... needs to be fixed manually.")
        sys.exit(1)

    # Find additional vlans the host needs to connect to
    tagged_vlans = []
    for vlan_type in ('public1', 'analytics1'):
        additional_vlan_name = f"{vlan_type}-{private_vlan_location}-{host.site.slug}"
        additional_vlan = nb.ipam.vlans.get(name=additional_vlan_name)
        if additional_vlan is not None:
            tagged_vlans.append(additional_vlan)

    # Ensure switch port is configured correctly for these vlans
    if switch_int.mode.value != "tagged":
        switch_int.mode = 'tagged'
        switch_int.save()
        nb_changes = True
        print(f"Netbox: {switch} interface {switch_int} changed mode to tagged.")
    tagged_vlan_ids = set([vlan.id for vlan in tagged_vlans])
    if tagged_vlan_ids != set([vlan.id for vlan in switch_int.tagged_vlans]):
        switch_int.tagged_vlans = list(tagged_vlan_ids)
        switch_int.save()
        nb_changes = True
        print(f"Netbox: {switch} interface {switch_int} tagged vlans set to {tagged_vlans}")

    # Generate /etc/network/interfaces config from Jinja template
    file_loader = FileSystemLoader(searchpath="./")
    env = Environment(loader=file_loader)
    template = env.get_template('interfaces.j2')
    output = template.render(host=host.name,
                             bridge_names = ['private'] + [vlan.name.split('-')[0].rstrip('1') for vlan in tagged_vlans],
                             primary_ip4 = host.primary_ip4,
                             primary_ip6 = host.primary_ip6,
                             ip6_token = f"::{':'.join(str(host.primary_ip6).split('/')[0].split(':')[-4:])}",
                             v4_gateway = ipaddress.ip_interface(host.primary_ip4).network[1],
                             dns_search = f"{host.site.slug}.wmnet",
                             physical_int = physical_int,
                             tagged_vlans = tagged_vlans)

    filename = f"{args.host}.txt"
    with open(filename, 'w') as f:
        f.write(output)
    if args.verbose:
        print("*******************************************************\n")
        print(output)
        print("\n*******************************************************")
    else:
        print(f'The /etc/network/interfaces config has been written to {filename}')
    if nb_changes:
        print("NOTE: Netbox vlan settings were updated, please run sre.network.configure-switch-interfaces cookbook.")


def get_switch_int(nb_host):
    """ Returns switch and interface object for a given server primary link """
    ip_int = nb.dcim.interfaces.get(name=nb_host.primary_ip4.assigned_object, device_id=nb_host.id)
    if ip_int.type.value == "bridge":
        physical_int = nb.dcim.interfaces.get(device_id=nb_host.id, bridge_id=ip_int.id,
                                              type__n=('virtual', 'lag', 'bridge'), mgmt_only=False)
    else:
        physical_int = ip_int

    switch = nb.dcim.devices.get(name=physical_int.connected_endpoints[0].device.name)
    switch_int = nb.dcim.interfaces.get(device_id=switch.id, name=physical_int.connected_endpoints[0].name)
    return physical_int, switch, switch_int


if __name__=="__main__":
    main()
