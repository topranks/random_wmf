#!/usr/bin/python3

from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import pynetbox
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

import json

import re

def main():
    passwd = getpass(prompt="iDRAC Password: ")

    server='https://cloudservices1006.mgmt.eqiad.wmnet'

    for server in servers:
        mgmt_int = nb.dcim.interfaces.get(device_id=server.id, name="mgmt")
        mgmt_hostname  = nb.ipam.ip_addresses.get(interface_id=mgmt_int.id).dns_name

        print(mgmt_hostname)

        break

        url = f"https://{mgmt_ip}/redfish/v1/Managers/iDRAC.Embedded.1"
        resp = requests.get(url, verify=False, auth=HTTPBasicAuth('root', passwd), 
            timeout=(15, 90))

        if resp.status_code == 404:
            print("API endpoint not found (404)")
        else: 
            print(f"{server.name}, {resp.json()['FirmwareVersion']}")


if __name__=="__main__":
    main()


