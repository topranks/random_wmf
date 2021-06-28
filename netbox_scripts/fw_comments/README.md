### fw_comments.py

This is a simple script that reads a file from disk that contains a Juniper filter configuration (in "display set" command format) and prints it back to the screen with information added in-line about IP addresses found in the filter.

#### Dependencies

Requires [PyNetbox](https://github.com/netbox-community/pynetbox)

#### Arguments

|Name|Descr|
|----|-----|
|-n, --netbox|Netbox server / IP|
|-k, --key|API token for Netbox|
|-f, --file|File name containing JunOS filter "set" commands|


#### Example

```
cmooney@testvm:~$ cat example_filter 
set firewall family inet filter test_filter term example_term1 from destination-address 10.72.0.181/32
set firewall family inet filter test_filter term example_term1 then accept
set firewall family inet filter test_filter term example_term2 from destination-address 10.72.16.30/32
set firewall family inet filter test_filter term example_term2 then accept
cmooney@testvm:~$ 
cmooney@testvm:~$ 
cmooney@testvm:~$ fw_comments.py --file example_filter --key <mykey>

set firewall family inet filter test_filter term example_term1 from destination-address 10.72.0.181/32  # machine1 - eno1 (machine1.example)
set firewall family inet filter test_filter term example_term1 then accept

set firewall family inet filter test_filter term example_term2 from destination-address 10.72.16.30/32  # machine2 - eno3 (machine2.example)
set firewall family inet filter test_filter term example_term2 then accept
```
