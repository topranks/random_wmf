== Spine/Leaf netbox allocator script ==

Used to add Netbox elements for WMF spine/leaf networks, based on Juniper QFX interface naming.

Defaults to working backwars on LEAF devices from port et-0/0/55 adding a connection to all SPINES.

Adds links, link addressing, loopbacks (underlay & overlay), loopback addressing, per-rack private Vlan, subnets for each vlan and irb GW interfaces for same.  Also takes care of DNS fields for IP allocations.  If an element already exists (say a loopback interface) then it will skip that, so it can be re-run even if some elements already exist (be careful has not been thoroughly tested).

Prior to running all devices should be present in Netbox.  The script reads a YAML file which defines the parameters for it to run.  This file should define the following:
```
devices:
  spine: <list of spine devices that belong to the fabric>
  leaf: <list of leaf devices that belong to fabric>
```

Various IPv4/IPv6 subnets need to be included, which are used to assign sub-objects (child prefixes and IP addresses) for the various elements.  Each subnet needs to be a defined Netbox prefix as the script uses the available_ips() and available_prefixes() functions.

```
subnets:
  underlay_links: <ipv4 prefix from which to pick /31 link IP addressing for the underlay>
  underlay_loopbacks: <ipv4 prefix from which to pick /32 IPs for the lo0.0 interface>
  overlay_loopback4: <ipv4 prefix from which to pick /32 IPs for the lo0.5000 interface in vrf PRODUCTION>
  overlay_loopback6: <ipv6 prefix from which to pick /128 IPs for the lo0.5000 interface in vrf PRODUCTION>
  vlan4: <ipv4 parent prefix to pick per-device /24 private subnets from>
  vlan6: <ipv6 parent prefix to pick per-device /64 private subnets from>
```

Additonally you need to specify the "start" vlan.  Vlans will be added sequentially starting with this ID, skipping any that are already in use.

```
vlans:
  vlan_start: 2019
```

Spine ports are allocated starting at et-0/0/0 and working up.  Any interfaces that don't exist will be created as QSFP28 ports in the process.  If for some reason we wish to skip certain port numbers on the Spines we can list them under 'skip_spine_int'

```
skip_spine_int:
  - 8
```

