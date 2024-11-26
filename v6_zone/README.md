
# gdnsd zone file 'INCLUDE' generator for Netbox-generated IPv6 PTR snippets

# Determines relative $ORIGIN based on the zone file itself, and then adds the 
# INCLUDE for the /64 

Usage:

./gen_v6_reverse.py -p 2620:0:861:3::/64,2a02:ec80:300:2::/64 -k <netbox_api_token> -d <path_to_dnsrepo_templates_dir>


**** 1.6.8.0.0.0.0.0.0.2.6.2.ip6.arpa ****

; Vlan 1003 - public1-c-eqiad
$ORIGIN 3.0.0.0.@Z
$INCLUDE netbox/3.0.0.0.1.6.8.0.0.0.0.0.0.2.6.2.ip6.arpa


**** 0.8.c.e.2.0.a.2.ip6.arpa ****

; Vlan 312 - public1-by27-esams
$ORIGIN 2.0.0.0.0.0.3.0.@Z
$INCLUDE netbox/2.0.0.0.0.0.3.0.0.8.c.e.2.0.a.2.ip6.arpa


Netbox API tokens can be generated at https://netbox.wikimedia.org/user/api-tokens/

