#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

'''
Input data example:

cloudcephosd2002-dev	1	asw-b1-codfw ge-1/0/0	cloudsw1-b1-codfw ge-0/0/0
cloudcephosd2002-dev	1	asw-b1-codfw ge-1/0/12	cloudsw1-b1-codfw ge-0/0/22
cloudvirt2002-dev	2	asw-b1-codfw ge-1/0/2	cloudsw1-b1-codfw ge-0/0/1
cloudvirt2001-dev	4	asw-b1-codfw ge-1/0/6	cloudsw1-b1-codfw ge-0/0/3
'''

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    with open("cloudsw_ints.txt", "r") as input_file:
        for line in input_file.readlines():
            splitline = line.split()
            print(splitline[0])
            device = nb.dcim.devices.get(name=splitline[0])
            old_sw = nb.dcim.devices.get(name=splitline[2])
            old_sw_int = nb.dcim.interfaces.get(name=splitline[3], device_id=old_sw.id)
            old_cable = old_sw_int.cable
            old_sw_int_type = old_sw_int.type.value
            old_sw_int_mode = old_sw_int.mode.value
            untagged_vlan = old_sw_int.untagged_vlan.id
            tagged_vlans = [vlan.id for vlan in old_sw_int.tagged_vlans]
            server_int = old_sw_int.connected_endpoint
            cable_color = old_sw_int.cable.color
            cable_type = old_sw_int.cable.type
            new_sw = nb.dcim.devices.get(name=splitline[4])
            host_int_id = old_cable.termination_b_id
            new_sw_int_name = splitline[5]

            host_int = nb.dcim.interfaces.get(id=host_int_id)
            if host_int.device.name != splitline[0]:
                # server is other end of cable
                host_int_id = old_cable.termination_a_id
                host_int2 = nb.dcim.interfaces.get(id=host_int_id)
                if host_int2.device.name != splitline[0]:
                    print(f"  ERROR: {splitline[0]} does not match device at either end of existing switch cable")
                    sys.exit(1)
 
            print(f"  Creating {new_sw.name} {new_sw_int_name}")
            new_sw_int = nb.dcim.interfaces.create(device=new_sw.id, name=new_sw_int_name,
                type=old_sw_int_type, mtu=9192, mode=old_sw_int_mode, 
                untagged_vlan=untagged_vlan, tagged_vlans=tagged_vlans)

            print(f"  Deleting cable {old_cable}")
            old_cable.delete()

            new_cable = nb.dcim.cables.create(termination_a_type='dcim.interface', termination_a_id=host_int_id,
                termination_b_type='dcim.interface', termination_b_id=new_sw_int.id, color=cable_color, type=cable_type,
                status="connected")
            print(f"  Created cable {new_cable}")

            print(f"  Defaulting {old_sw.name} {old_sw_int.name}")
            # Default old switch int vars and disable
            old_sw_int.enabled = False
            old_sw_int.mtu = None
            old_sw_int.mode = None
            old_sw_int.tagged_vlans = []
            old_sw_int.untagged_vlan = None
            old_sw_int.save()
            print()


if __name__=="__main__":
    main()

