#!/usr/bin/python3

import requests
import json
from pprintpp import pprint as pp
import argparse
import pynetbox
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
args = parser.parse_args()


def main():
    fhrp_groups = get_fhrp_groups("a-eqiad")
    fhrp_groups = get_fhrp_groups("b-eqiad")
    fhrp_groups = get_fhrp_groups("c-eqiad")
    fhrp_groups += get_fhrp_groups("d-eqiad")

    nb = get_nb()

    for fhrp_group in fhrp_groups:
        row = fhrp_group['description'].split("-")[1]
        if row in ("a", "c"):
            primary = "cr1-eqiad"
        else:
            primary = "cr2-eqiad"
        for interface in fhrp_group['fhrpgroupassignment_set']:
            priority = 110 if interface['interface']['device']['name'] == primary else 90
            if interface['priority'] != priority:
                nb_group = nb.ipam.fhrp_group_assignments.get(id=interface['id'])
                nb_group.priority = priority
                nb_group.save()
                print(f"{interface['interface']['device']['name']} {interface['interface']['name']} ({fhrp_group['description']}) changed pririty from {interface['priority']} to {priority}")

def get_fhrp_groups(site: str) -> list:
    """Gets fhrp groups with description containing 'site'"""

    fhrp_query = f"""
        query get_fhrp_groups {{
          fhrp_group_list(filters: {{description: {{i_contains: "{site}"}}}}) {{
            id
            description
            fhrpgroupassignment_set {{
              id
              priority
                interface{{
                ... on InterfaceType {{
                  id
                  name
                  device {{
                    id
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
    """

    return get_graphql_query(fhrp_query)['fhrp_group_list']


def get_graphql_query(query: str) -> dict:
    """Sends graphql query to netbox and returns JSON result as dict"""
    url = f"https://{args.netbox}/graphql/"
    headers = {
        'Authorization': f'Token {args.key}',
        'User-Agent': 'Cathal Script'
    }
    data = {"query": query}
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


def get_nb():
    nb_url = "https://{}".format(args.netbox)
    nb = pynetbox.api(nb_url, token=args.key)
    http_session = requests.Session()
    http_session.headers.update({'User-Agent': f'Cathal Script'})
    nb.http_session = http_session
    return nb

if __name__ == "__main__":
    main()
