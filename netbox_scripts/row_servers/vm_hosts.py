#!/usr/bin/python3

import argparse
import pynetbox
import string
import wikitextparser as wtp
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', help='File with output of gnt-instance list', type=str, required=True)
parser.add_argument('-t', '--teamsfile', help='Mark-up of teams responsible for server types', type=str)
parser.add_argument('-g', '--group', help='Group by Ganetti host', default=False, action='store_true')
args = parser.parse_args()

def main():

    if args.teamsfile:
        server_teams = get_server_teams()

    vms_by_host = {}
    
    with open(args.filename, 'r') as filename:
        for line in filename.readlines():
            if "kvm" in line:
                words = line.split()
                vm_name = words[0].split(".")[0]
                host = words[3].split(".")[0]
                if host in vms_by_host.keys():
                    vms_by_host[host].append(vm_name)
                else:
                    vms_by_host[host] = [vm_name]


    if args.group:
        print("|Ganeti Host     |VM Name             |Team                                                          |Action Required |")
        print("|----------------|--------------------|--------------------------------------------------------------|----------------|")
        for host, vms in vms_by_host.items():
            for vm in vms:
                vm_type = vm.rstrip(string.digits)
                if vm_type in server_teams:
                    team = server_teams[vm_type]
                else:
                    team = ""

                print("|{:16}|{:20}|{:62}||".format(host, vm, team))
    else:
        print("|VM Name             |Ganeti Host     |Team                                                          |Action Required  |")
        print("|--------------------|----------------|--------------------------------------------------------------|----------------------|")

        vm_hosts = {}
        for host, vms in vms_by_host.items():
            for vm in vms:
                vm_hosts[vm] = host

        sorted_vms = sorted(vm_hosts.items(), key=lambda x:x[0])

        for vm in sorted_vms:
            vm_type = vm[0].rstrip(string.digits)
            if vm_type in server_teams:
                team = server_teams[vm_type]
            else:
                team = ""

            print("|{:20}|{:16}|{:62}||".format(vm[0], vm[1], team))



def get_server_teams():
    server_teams = {}

    with open(args.teamsfile, 'r') as teamsfile:
        wikitable = wtp.parse(teamsfile.read()).tables[0].data()

    for server_type_details in wikitable:
        server_teams[server_type_details[0]] = server_type_details[-1]

    return server_teams
            

if __name__=="__main__":
    main()

