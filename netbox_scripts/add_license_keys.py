#!/usr/bin/python3

import argparse
import pynetbox
import os

from pprintpp import pprint as pp

import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-d', '--directory', help='Path of directory with license files', required=True, type=str)
args = parser.parse_args()

def main():
    """ Adds licence keys to netbox.  Source directory should contain files with 
        naming convention: device - something.txt, for instance:
        
            lsw1-d8-codfw - license XH3723370208.txt
            ssw1-d1-codfw - license AO09010009.txt

    """    

    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)
    license_role = nb.dcim.inventory_item_roles.get(slug='license')
    manufacturer = nb.dcim.manufacturers.get(slug='juniper')
    
    licenses = {}
    for filename in os.listdir(args.directory):
        with open(os.path.join(args.directory, filename), 'r') as f:
            in_license = False
            license_key = ''
            for line in f.readlines():
                if not in_license:
                    if line.startswith("Feature"):
                        feature = line.split()[-1]
                    elif line.startswith("HW Serial Number"):
                        serial = line.split()[-1]
                    elif line.startswith("License Key"):
                        in_license = True
                else:
                    if line.startswith("J"):
                        splitline = line.split()
                        license_serial = splitline[0]
                        del splitline[0]
                        license_key = " ".join(splitline) + " "
                    elif license_key:
                        license_key += line.strip() + " "

            licenses[serial] = {}
            licenses[serial]['feature'] = feature
            licenses[serial]['filename'] = filename.split(" - ")[0]
            licenses[serial]['license_serial'] = license_serial
            licenses[serial]['license_key'] = license_key


    for device_serial, license_data in licenses.items():
        device = nb.dcim.devices.get(serial=device_serial)
        if not device:
            print(f"Not found in Netbox: {device_serial} - {license_data['filename']}")
            continue

        print(device.name)
        if device.name != license_data['filename']:
            print("WARNING: Filename {license_data['filename']} doesn't match device name {device.name}")

        # Create inventory item with the license details
        inv_item = nb.dcim.inventory_items.create(device=device.id, name='license', role=license_role.id, 
            manufacturer=manufacturer.id, serial=license_data['license_serial'], description=license_data['feature'],
            custom_fields={'license_key': license_data['license_key']})

if __name__=="__main__":
    main()

