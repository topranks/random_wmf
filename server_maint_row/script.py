from collections import defaultdict
	from pprint import pprint
	import re
	servers_per_teams = defaultdict(list)
	for nodes, output in worker.get_results():
	    servers_per_teams[output.message().decode()[2:].replace('\n- ', ' and ')].extend(re.split('(?<![0-9]),',str(nodes), flags=re.IGNORECASE))
	
	pprint(servers_per_teams)
	
	phab_tag = {'Traffic': '#traffic',
		    'Infrastructure Foundations': '#infrastructure-foundations',
		    'WMCS': '#cloud-services-team',
		    'ServiceOps-Collab': '#serviceops-collab',
		    'Data Engineering': '#data-engineering',
		    'Search Platform': '#discovery-search',
		    'Observability': '#sre_observability',
		    'Core Platform': '#core-platform-team',
		    'Machine Learning': '#machine-learning-team',
		    'Data Persistence': '#data-persistence',
		    'ServiceOps': '#serviceops',
	           }
	
	for teams, servers_groups in servers_per_teams.items():
	    print(f"\n== {teams} ==")
	    for team in teams.split(' and '):
	    	print(f"{phab_tag[team]}", end=' ')
	    print("\n|Servers|Depool action needed|Repool action needed|Status|")
	    print("|---|---|---|---|")
	    for servers in servers_groups:
	    	servers_short = servers.replace('.codfw.wmnet', '').replace('.wikimedia.org', '')
	    	print(f"|{servers_short}| | | |")
