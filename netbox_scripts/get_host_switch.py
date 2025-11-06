#!/usr/bin/python3

import argparse
import requests
import sys
import pynetbox

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--netbox', help='Netbox server IP / Hostname', type=str, default="netbox.wikimedia.org")
parser.add_argument('-k', '--key', help='API Token / Key', required=True, type=str)
parser.add_argument('-s', '--site', help='site (i.e. eqiad)', required=True, type=str)
parser.add_argument('-r', '--row', help='row (i.e. b or a,b,c)', required=True, type=str)
args = parser.parse_args()

def main():
    nb = get_nb()
    # Get locations from the row letters and format so it can be used in graphql query
    location_names = [f"{args.site}-row-{row}" for row in args.row.split(",")]
    locations = nb.dcim.locations.filter(site=args.site, slug=location_names)
    location_ids = [str(location.id) for location in locations]
    location_id_str = str(location_ids).replace("'", '"')

    servers = get_row_servers(location_id_str)
    for server in servers:
        try:
            print(f"{server['name']},{server['primary_ip4']['assigned_object']['connected_endpoints'][0]['device']['name']},"
                  f"{server['primary_ip4']['assigned_object']['connected_endpoints'][0]['name']}")
        except (TypeError, IndexError):
            print(f"{server['name']},ERROR,ERROR")


def get_row_servers(location_ids) -> list:
    """Gets all servers and their attached switch ports at location_id"""
    
    server_query = f"""
        query {{
          device_list(
            filters: {{
              role: "server"
              status: "active"
              location_id: {str(location_ids)}
            }}
          ) {{
            name
            primary_ip4 {{
              assigned_object {{
                ... on InterfaceType {{
                  connected_endpoints {{
                    ... on InterfaceType {{
                      name
                      device {{
                        name
                      }}
                    }}
                  }}
              }}
            }}
          }}
        }}
        }}
    """
    return get_graphql_query(server_query)['device_list']


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


if __name__=="__main__":
    main()

