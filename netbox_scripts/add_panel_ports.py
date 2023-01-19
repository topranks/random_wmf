#!/usr/bin/python3

import argparse
import pynetbox

parser = argparse.ArgumentParser(
    description="Adds patch panel front/rear ports to netbox in pattern module/port1-port2 (i.e. 2/3-4)",
    epilog="Example: ./add_panel_ports.py --panel 'panel1-4-eqsin' --modules 4 --pairs 12")
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', type=str)
parser.add_argument('-p', '--panel', help='Name of panel device in Netbox', required=True, type=str)
parser.add_argument('-m', '--modules', help='Number of individual patch panel modules in nb device (default 4)', type=int, default=4)
parser.add_argument('--pairs', help='Number of duplex fiber pairs in each module (default 12)', type=int, default=12)
args = parser.parse_args()


def main():
    nb_url = "https://{}".format(args.netbox)
    nb_key = get_nb_key()
    nb = pynetbox.api(nb_url, token=nb_key)

    panel = nb.dcim.devices.get(name=args.panel)

    for module in range(modules):
        for pair in range(pairs_per_module):
            port_name = f"{module + 1}/{(pair*2)+1}-{(pair*2)+2}"
            new_rear = nb.dcim.rear_ports.create(device=panel.id, name=port_name, type="lc")
            new_front = nb.dcim.front_ports.create(device=panel.id, name=port_name, type="lc", rear_port=new_rear.id)
            print(port_name)


def get_nb_key():
    if args.key:
        return args.key
    else:
        from getpass import getpass
        return getpass(prompt="Netbox API Key: ")


if __name__=="__main__":
    main()


