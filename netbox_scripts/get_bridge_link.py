#!/usr/bin/python3

import pynetbox
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    '''
    device = nb.dcim.devices.get(name='ganeti-test2001')

    hype_iface = device.primary_ip.assigned_object
    print(hype_iface.type.value)

    phys_iface = nb.dcim.interfaces.get(device_id=device.id, type__n=('virtual', 'lag', 'bridge'), mgmt_only=False, bridge_id=hype_iface.id)
  

    print(phys_iface.connected_endpoint.device_type)

    #.device.device_type.model.lower())
    '''

    device = nb.dcim.devices.get(name='sretest2003')


    int_from_ip = device.primary_ip.assigned_object

    int_obj = nb.dcim.interfaces.get(device_id=device.id, name='eno1')


    switch1 = nb.dcim.devices.get(id=int_from_ip.connected_endpoint.device.id) 
    switch2 = nb.dcim.devices.get(id=int_obj.connected_endpoint.device.id)

   
    print(switch2.device_type.model.lower())


if __name__=="__main__":
    main()

