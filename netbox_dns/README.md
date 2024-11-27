
## Netbox zonefile snippet record generator v2

Just an example of how we can generate all the DNS names we need from
Netbox without as much complication as we have now.

The general approach is described in this [Phabricator task](https://phabricator.wikimedia.org/T362985)

In brief the approach is:

#### 1. We take the set of zones we are auth for and map each Netbox record to the appropriate one

#### 2. For each of them we add a single INCLUDE, at the zone "apex"

For instance:
```
$ORIGIN @Z
$INCLUDE snippets/wikimedia.org
```

#### 3. The snippet file this points to contains all the Netbox records for the zone

#### 4. No "ORIGIN" directives are used within the snippet files
 
For instance we have entries like this in the zone file for 'wmnet':
```
kafka-main1006.eqiad                     IN A       10.64.0.101
```

Instead of:
```
$ORIGIN eqiad.@Z
kafka-main1006                           IN A       10.64.0.101
```

This is more of a style thing than anything, but it keeps the automation cleaner and simpler.

The ORIGIN directives can of course still be used for manual entries in the zonefiles themselves, 
but when automating the creation of the snippets it seems simpler and less error-prone to just 
put the full records in.

### Running this script

The script is fairly easy to run.  It does need a local copy of the dns repo so it can list 
the files and compile a list of zone names we are auth for from that.  This path can be 
passed as a command-line argument, as can a Netbox API key to allow it to get the IP 
records from Netbox.

Thanks to GraphQL it runs quickly, generating all the records in only a few seconds:
```
cmooney@wikilap:~$ time ./gen_zonefile_includes.py --key <netbox_api_token> --dns_repo <path_to_template_dir>
Skipping reverse for 27.111.227.106/29 as it doesn't fit into any zone we are auth for
Skipping reverse for 149.97.228.94/30 as it doesn't fit into any zone we are auth for
Skipping reverse for 177.185.14.4/29 as it doesn't fit into any zone we are auth for
Skipping reverse for 185.27.16.142/29 as it doesn't fit into any zone we are auth for
Skipping reverse for 193.251.154.146/31 as it doesn't fit into any zone we are auth for
Skipping reverse for 198.24.47.102/30 as it doesn't fit into any zone we are auth for
Skipping reverse for 216.117.46.36/29 as it doesn't fit into any zone we are auth for
Skipping reverse for 2001:688:0:4::2d4/127 as it doesn't fit into any zone we are auth for
Skipping reverse for 2403:b100:3001:9::2/64 as it doesn't fit into any zone we are auth for
Skipping reverse for 2607:f6f0:1000:1194::2/64 as it doesn't fit into any zone we are auth for
Skipping reverse for 2607:fb58:9000:7::2/64 as it doesn't fit into any zone we are auth for
Skipping reverse for 2804:ad4:ff12:19::84/121 as it doesn't fit into any zone we are auth for
Skipping reverse for 2a00:1188:5:e::4/64 as it doesn't fit into any zone we are auth for

Wrote output files into snippet dir.

real	0m2.370s
user	0m0.526s
sys	0m0.031s
```



