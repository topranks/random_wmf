
## Netbox zonefile snippet record generator v2

Just an example of how we can generate all the DNS names we need from
Netbox without as much complication as we have now.

The general approach is described in [Phabricator](https://phabricator.wikimedia.org/T362985)

In brief what we would do is:

* For every zone we have netbox-based records for we add a single INCLUDE, at the zone "apex".

For instance:
```
$ORIGIN @Z
$INCLUDE snippets/wikimedia.org
```

* This script generates one file for each zone we have records in Netbox for, and adds all the 
entries that belong to it to that single file.

* No "ORIGIN" directives are used within the snippet files for simplicity, instead the full set 
of labels relative to the zone the record is being placed in are used.
 
For instance we have this in the snippet file for 'wmnet':
```
kafka-main1006.eqiad                     IN A       10.64.0.101
```

Instead of:
```
$ORIGIN eqiad.@Z
kafka-main1006                           IN A       10.64.0.101
```

The ORIGIN directives can of course still be used for manual entries in the zonefiles themselves, 
but when automating the creation of the snippets it seems simpler and less error-prone to just 
put the full records in.

