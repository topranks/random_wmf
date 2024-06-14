#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-4', help='Anycast IPv4 address in CIDR format (defaults to first IP in subnet)', type=str)
parser.add_argument('-6', help='Anycast IPv6 address in CIDR format (defaults to first IP in subnet)', type=str)
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-r', '--row', help='Row of LEAF switches to add gw to', type=str, required=True)
parser.add_argument('-s', '--site', help='Site of swtiches to add gw to', type=str, required=True)
parser.add_argument('-u', '--unicast', help='Add a unicast IP to each interface also', default=False, action='store_true')
parser.add_argument('-v', '--vlan', help='Vlan ID of IRB sub-int', type=int, required=True)
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    """Adds anycast GW device to switches"""

    nb_url = "https://{}".format(args.netbox)
    global nb
    nb = pynetbox.api(nb_url, token=args.key)

    row = nb.dcim.locations.get(name=f"{args.site} row {args.row.upper()}")
    vlan = nb.ipam.vlans.get(vid=args.vlan)

    gw_ips = {}
    for family in (4, 6):
        gw_ips[family] = getattr(args, str(family))
        if gw_ips[family] is None:
            gw_ips[family] = get_vlan_gw(vlan.id, family)

    ip_obj = ipaddress.ip_interface(gw_ips[4])
    if ip_obj.is_private:
        dns_suffix = f"{args.site}.wmnet"
    else:
        dns_suffix = "wikimedia.org"

    irb_name = f"irb.{args.vlan}"
    anycast_dns_name = f"anycast-gw-{args.vlan}-{args.site}.{dns_suffix}"

#    devices = nb.dcim.devices.filter(name__isw='lsw', location_id=row.id, role_id=4, status="active")
    devices = nb.dcim.devices.filter(name__isw='ssw1-a')
    for device in devices:
        # Try to get interface, if it already exists we skip
        interface = nb.dcim.interfaces.get(device_id=device.id, name=irb_name)
        if interface is not None:
            print(f"Skipping {device.name} - interface {irb_name} already exists.")
            continue

        irb_int = nb.dcim.interfaces.create(device=device.id,
                                            name=irb_name,
                                            description=f"Subnet {vlan.name}",
                                            vrf=2,
                                            type="virtual")
        print(f"Created {irb_name} on {device.name}.")

        # Create instance anycast IP and attach to interface
        for addr_fam, gw_ip in gw_ips.items():
            anycast_addr = nb.ipam.ip_addresses.create(address=gw_ip,
                        assigned_object_type="dcim.interface",
                        assigned_object_id=irb_int.id,
                        dns_name=anycast_dns_name,
                        role="anycast")
            print(f"  Added IP {gw_ip} to {irb_name} on {device.name} with name {anycast_dns_name}.")

            # If we also want to add a unique per-device IP
            if args.unicast:
                unicast_dns_name = f"{irb_name.replace('.','-')}.{device.name}.{dns_suffix}"
                nb_prefix = nb.ipam.prefixes.get(vlan_id=vlan.id, family=addr_fam)
                unique_addr = nb_prefix.available_ips.create()
                unique_addr.assigned_object_type = "dcim.interface"
                unique_addr.assigned_object_id = irb_int.id
                unique_addr.dns_name = unicast_dns_name
                unique_addr.save()
                print(f"  Added IP {unique_addr} to {irb_name} on {device.name} with name {unicast_dns_name}.")

                
def get_vlan_gw(vlan_id, addr_fam):
    pfx = nb.ipam.prefixes.get(vlan_id=vlan_id, family=addr_fam)
    ip_subnet = ipaddress.ip_network(pfx)
    return f"{ip_subnet[1]}/{ip_subnet.prefixlen}"


if __name__=="__main__":
    main()

