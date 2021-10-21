#!/usr/bin/python3

import argparse
import pynetbox
import string
import wikitextparser as wtp
import sys
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-s', '--site', help='Netbox site name', type=str, required=True)
parser.add_argument('-t', '--teamsfile', help='Mark-up of teams responsible for server types', type=str)
args = parser.parse_args()

def main():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)

    if args.teamsfile:
        server_teams = get_server_teams()

    req_teams = set()

    site = nb.dcim.sites.get(slug=args.site)
    if site:
        servers = nb.dcim.devices.filter(site_id=site.id, status="active", role="server")
        server_names = []
        server_types = {}
        for server in servers:
            server_names.append(server.name)
            server_type = server.name.rstrip(string.digits)
            if server_type in server_types.keys():
                server_types[server_type] += 1
            else:
                server_types[server_type] = 1

        sorted_types = sorted(server_types.items(), key=lambda x:x[1], reverse=True)

        if args.teamsfile:
            print("|Server Name / Prefix    |Count|Relevant Team                                                 |Action Required |")
            print("|----------------------|-----|----------------------------------------------------------------|----------------|")
        else:
            print("|Server Name / Prefix    |Count|Action Required|")
            print("|----------------------|-----|----------------|")
        for server_type in sorted_types:
            if server_type[1] == 1:
                server_name = list(filter(lambda x: x.startswith(server_type[0]), server_names))[0]
            else:
                server_name = server_type[0]
            if args.teamsfile:
                if server_type[0] in server_teams.keys():
                    team_name = server_teams[server_type[0]]
                    req_teams.add(team_name)
                else:
                    team_name = ""
                print("|{:24}|{:<5}|{:64}||".format(server_name, server_type[1], team_name))
            else:
                print("|{:24}|{:<5}||".format(server_name, server_type[1]))

        print()
        for team in req_teams:
            print(team)
            
                
    else:
        print("No site \"{}\" found.. make sure to use correct slug as in Netbox.".format(args.site))
        sys.exit(1)

def get_server_teams():
    server_teams = {}

    with open(args.teamsfile, 'r') as teamsfile:
        wikitable = wtp.parse(teamsfile.read()).tables[0].data()

    for server_type_details in wikitable:
        server_teams[server_type_details[0]] = server_type_details[-1]

    return server_teams
            
            

if __name__=="__main__":
    main()

