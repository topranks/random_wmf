#!/usr/bin/python3

import argparse
import pynetbox
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox-next.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    new_cable = nb.dcim.cables.create(termination_a_type='dcim.interface', termination_a_id=10015,
        termination_b_type='dcim.interface', termination_b_id=28360, color="ff66ff", type="cat5e",
        status="connected")


if __name__=="__main__":
    main()

