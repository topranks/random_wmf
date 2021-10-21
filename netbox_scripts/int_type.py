#!/usr/bin/python3

import pynetbox
from getpass import getpass

netbox_key = getpass(prompt="Netbox API Key: ")
nb_url = "https://netbox.wikimedia.org"
nb = pynetbox.api(nb_url, token=netbox_key)

router = nb.dcim.devices.get(name='mr1-ulsfo')
interfaces = nb.dcim.interfaces.filter(device_id=router.id)

for interface in interfaces:
    print("{} - {} - {}".format(interface.name, interface.type.label, interface.type.value))

