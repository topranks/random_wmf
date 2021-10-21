#!/usr/bin/python3

from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
import urllib3
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

import json

import re

def main():
    passwd = getpass(prompt="iDRAC Password: ")
    r430_list = open('dell_r430.txt', 'r')

    for r430 in r430_list.readlines():
        dell_host = r430.rstrip("\n")
        try:
            print("{}: ".format(dell_host), end = '', flush=True)
            url = "https://{}/redfish/v1/Managers/iDRAC.Embedded.1".format(dell_host)
            resp = requests.get(url, verify=False, auth=HTTPBasicAuth('root', passwd), 
                timeout=(15, 90))

            if resp.status_code == 404:
                print("API endpoint not found (404)")
            else: 
                print(resp.json()['FirmwareVersion'])

        except Exception as e:
            print(type(e).__name__)

    r430_list.close()


if __name__=="__main__":
    main()


