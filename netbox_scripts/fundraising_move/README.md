# Fundraising move script

Example:
```
me@laptop:~$ ./fundraising_move.py -k <key> -n netbox-next.wikimedia.org 
Getting data... 
civi1002 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/5 on fasw2-e16a-eqiad... done.
Deleting old cable from civi1002 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/5... done.
Deleting old interface ge-0/0/5 on fasw2-c1a-eqiad... done.
Creating new cable from civi1002 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/5... done.
Creating new interface ge-0/0/5 on fasw2-e16b-eqiad... done.
Deleting old cable from civi1002 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/5... done.
Deleting old interface ge-0/0/5 on fasw2-c1b-eqiad... done.
Creating new cable from civi1002 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/5... done.

fran1002 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/40 on fasw2-e16a-eqiad... done.
Deleting old cable from fran1002 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/40... done.
Deleting old interface xe-0/0/40 on fasw2-c1a-eqiad... done.
Creating new cable from fran1002 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/40... done.
Creating new interface xe-0/0/40 on fasw2-e16b-eqiad... done.
Deleting old cable from fran1002 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/40... done.
Deleting old interface xe-0/0/40 on fasw2-c1b-eqiad... done.
Creating new cable from fran1002 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/40... done.

franio1001 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/37 on fasw2-e16a-eqiad... done.
Deleting old cable from franio1001 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/37... done.
Deleting old interface xe-0/0/37 on fasw2-c1a-eqiad... done.
Creating new cable from franio1001 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/37... done.
Creating new interface xe-0/0/37 on fasw2-e16b-eqiad... done.
Deleting old cable from franio1001 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/37... done.
Deleting old interface xe-0/0/37 on fasw2-c1b-eqiad... done.
Creating new cable from franio1001 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/37... done.

franio1002 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/36 on fasw2-e16a-eqiad... done.
Deleting old cable from franio1002 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/36... done.
Deleting old interface xe-0/0/36 on fasw2-c1a-eqiad... done.
Creating new cable from franio1002 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/36... done.
Creating new interface xe-0/0/36 on fasw2-e16b-eqiad... done.
Deleting old cable from franio1002 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/36... done.
Deleting old interface xe-0/0/36 on fasw2-c1b-eqiad... done.
Creating new cable from franio1002 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/36... done.

franio1003 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/35 on fasw2-e16a-eqiad... done.
Deleting old cable from franio1003 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/35... done.
Deleting old interface xe-0/0/35 on fasw2-c1a-eqiad... done.
Creating new cable from franio1003 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/35... done.
Creating new interface xe-0/0/35 on fasw2-e16b-eqiad... done.
Deleting old cable from franio1003 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/35... done.
Deleting old interface xe-0/0/35 on fasw2-c1b-eqiad... done.
Creating new cable from franio1003 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/35... done.

franio1004 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/32 on fasw2-e16a-eqiad... done.
Deleting old cable from franio1004 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/32... done.
Deleting old interface xe-0/0/32 on fasw2-c1a-eqiad... done.
Creating new cable from franio1004 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/32... done.
Creating new interface xe-0/0/32 on fasw2-e16b-eqiad... done.
Deleting old cable from franio1004 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/32... done.
Deleting old interface xe-0/0/32 on fasw2-c1b-eqiad... done.
Creating new cable from franio1004 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/32... done.

fransc1001 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/42 on fasw2-e16a-eqiad... done.
Deleting old cable from fransc1001 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/42... done.
Deleting old interface xe-0/0/42 on fasw2-c1a-eqiad... done.
Creating new cable from fransc1001 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/42... done.
Creating new interface xe-0/0/42 on fasw2-e16b-eqiad... done.
Deleting old cable from fransc1001 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/42... done.
Deleting old interface xe-0/0/42 on fasw2-c1b-eqiad... done.
Creating new cable from fransc1001 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/42... done.

fransw1001 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/38 on fasw2-e16a-eqiad... done.
Deleting old cable from fransw1001 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/38... done.
Deleting old interface xe-0/0/38 on fasw2-c1a-eqiad... done.
Creating new cable from fransw1001 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/38... done.
Creating new interface xe-0/0/38 on fasw2-e16b-eqiad... done.
Deleting old cable from fransw1001 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/38... done.
Deleting old interface xe-0/0/38 on fasw2-c1b-eqiad... done.
Creating new cable from fransw1001 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/38... done.

frauth1002 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frav1003 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frban1002 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/41 on fasw2-e16a-eqiad... done.
Deleting old cable from frban1002 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/41... done.
Deleting old interface xe-0/0/41 on fasw2-c1a-eqiad... done.
Creating new cable from frban1002 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/41... done.
Creating new interface xe-0/0/41 on fasw2-e16b-eqiad... done.
Deleting old cable from frban1002 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/41... done.
Deleting old interface xe-0/0/41 on fasw2-c1b-eqiad... done.
Creating new cable from frban1002 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/41... done.

frbast1002 is in vlan frack-bastion1-c-eqiad - moving to rack E15... done.

frdata1002 is in vlan frack-listenerdmz1-c-eqiad - moving to rack E15... done.

frdb1004 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/10 on fasw2-e16a-eqiad... done.
Deleting old cable from frdb1004 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/10... done.
Deleting old interface ge-0/0/10 on fasw2-c1a-eqiad... done.
Creating new cable from frdb1004 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/10... done.
Creating new interface ge-0/0/10 on fasw2-e16b-eqiad... done.
Deleting old cable from frdb1004 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/10... done.
Deleting old interface ge-0/0/10 on fasw2-c1b-eqiad... done.
Creating new cable from frdb1004 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/10... done.

frdb1005 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/4 on fasw2-e16a-eqiad... done.
Deleting old cable from frdb1005 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/4... done.
Deleting old interface ge-0/0/4 on fasw2-c1a-eqiad... done.
Creating new cable from frdb1005 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/4... done.
Creating new interface ge-0/0/4 on fasw2-e16b-eqiad... done.
Deleting old cable from frdb1005 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/4... done.
Deleting old interface ge-0/0/4 on fasw2-c1b-eqiad... done.
Creating new cable from frdb1005 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/4... done.

frdb1006 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/15 on fasw2-e16a-eqiad... done.
Deleting old cable from frdb1006 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/15... done.
Deleting old interface ge-0/0/15 on fasw2-c1a-eqiad... done.
Creating new cable from frdb1006 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/15... done.
Creating new interface ge-0/0/15 on fasw2-e16b-eqiad... done.
Deleting old cable from frdb1006 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/15... done.
Deleting old interface ge-0/0/15 on fasw2-c1b-eqiad... done.
Creating new cable from frdb1006 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/15... done.

frdb1007 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface xe-0/0/39 on fasw2-e16a-eqiad... done.
Deleting old cable from frdb1007 PRIMARY_A to fasw2-c1a-eqiad xe-0/0/39... done.
Deleting old interface xe-0/0/39 on fasw2-c1a-eqiad... done.
Creating new cable from frdb1007 PRIMARY_A to fasw2-e16a-eqiad xe-0/0/39... done.
Creating new interface xe-0/0/39 on fasw2-e16b-eqiad... done.
Deleting old cable from frdb1007 PRIMARY_B to fasw2-c1b-eqiad xe-0/0/39... done.
Deleting old interface xe-0/0/39 on fasw2-c1b-eqiad... done.
Creating new cable from frdb1007 PRIMARY_B to fasw2-e16b-eqiad xe-0/0/39... done.

frdev1002 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/19 on fasw2-e16a-eqiad... done.
Deleting old cable from frdev1002 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/19... done.
Deleting old interface ge-0/0/19 on fasw2-c1a-eqiad... done.
Creating new cable from frdev1002 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/19... done.
Creating new interface ge-0/0/19 on fasw2-e16b-eqiad... done.
Deleting old cable from frdev1002 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/19... done.
Deleting old interface ge-0/0/19 on fasw2-c1b-eqiad... done.
Creating new cable from frdev1002 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/19... done.

frlog1002 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frmon1002 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frmx1001 is in vlan frack-listenerdmz1-c-eqiad - moving to rack E15... done.

frnetmon1002 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frpig1002 is in vlan frack-listenerdmz1-c-eqiad - moving to rack E15... done.

frpm1002 is in vlan frack-administration1-c-eqiad - moving to rack E15... done.

frqueue1003 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/21 on fasw2-e16a-eqiad... done.
Deleting old cable from frqueue1003 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/21... done.
Deleting old interface ge-0/0/21 on fasw2-c1a-eqiad... done.
Creating new cable from frqueue1003 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/21... done.
Creating new interface ge-0/0/21 on fasw2-e16b-eqiad... done.
Deleting old cable from frqueue1003 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/21... done.
Deleting old interface ge-0/0/21 on fasw2-c1b-eqiad... done.
Creating new cable from frqueue1003 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/21... done.

frqueue1004 is in vlan frack-fundraising1-c-eqiad - moving to rack E16... done.
Creating new interface ge-0/0/23 on fasw2-e16a-eqiad... done.
Deleting old cable from frqueue1004 PRIMARY_A to fasw2-c1a-eqiad ge-0/0/23... done.
Deleting old interface ge-0/0/23 on fasw2-c1a-eqiad... done.
Creating new cable from frqueue1004 PRIMARY_A to fasw2-e16a-eqiad ge-0/0/23... done.
Creating new interface ge-0/0/23 on fasw2-e16b-eqiad... done.
Deleting old cable from frqueue1004 PRIMARY_B to fasw2-c1b-eqiad ge-0/0/23... done.
Deleting old interface ge-0/0/23 on fasw2-c1b-eqiad... done.
Creating new cable from frqueue1004 PRIMARY_B to fasw2-e16b-eqiad ge-0/0/23... done.

pay-lb1001 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

pay-lb1002 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

payments1005 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

payments1006 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

payments1007 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

payments1008 is in vlan frack-payments1-c-eqiad - moving to rack E15... done.

```
