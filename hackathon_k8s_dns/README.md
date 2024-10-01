# Proof-of-concept reverse DNS delegation for k8s pod ranges

This is an example of how we might generate the required NS entries to 
go into the zone files on our authdns servers to delegate the IP blocks 
used by our kubernetes pods to the control-plane nodes of each cluster 
(these already run coredns and are authoritative for the sub-zones).

## Methodology

There are two input files used:

dns_k8s_reverse_delegation.yaml: This file needs to be built from the 
data in `hieradata/common/kubernetes.yaml`, exporting the 'cluster_cidr' 
and 'control_plane_nodes' information for each cluster.

dns_reverse_zones.yaml: This file contains a dict, keyed by an IP subnet,
with values representing the name of the zone file on our authdns servers 
for it.  It is used to find what zone the given NS records need to be 
placed for each subnet used by k8s.  This data is not already in hiera so 
we would need to add it, it's also not in Netbox exactly - as zones are cut 
at octet/nibble boundaries and the prefixes in netbox can be larger/smaller.

Taking these two input files we can run the 'generate_delegations2.py' 
script to parse them and generate the output shown in the 'output' directory.

## Next-steps

What we need to decide from here is how and where to do this work from.  I 
guess we could add the YAML files to our authdns servers, and generate the 
output using a systemd timer periodically?  The output files could be 
put into /etc/gdnsd/zones/k8s_delegations/ or some similar new directory, 
and we could then use INCLUDE statements in the actual zone files to 
include the data, running authdns-update to sync to all our hosts?

More than happy to listen to other suggestions of course.
