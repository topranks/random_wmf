#!/usr/bin/python3

import argparse
import pynetbox

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()

ports = ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12', '13-14', '15-16', '17-18', '19-20', '21-22', '23-24']
modules = 4

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    panel = nb.dcim.devices.get(name='EQIAD_F1_SMF_PANEL_1')

    for module in range(modules):
        for port in ports:
            port_name = f"{module + 1}/{port}"
            new_rear = nb.dcim.rear_ports.create(device=panel.id, name=port_name, type="lc")
            new_front = nb.dcim.front_ports.create(device=panel.id, name=port_name, type="lc", rear_port=new_rear.id)
            print(port_name)




if __name__=="__main__":
    main()

