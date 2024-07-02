#!/bin/bash
echo -n "SNMP RO Community: "
read -s COMMUNITY
echo
set -x
cd /srv/deployment/librenms/librenms
while read line;
do
    SITE=$(echo $line | awk -F"-" '{print $NF}')
    echo "$line.mgmt.$SITE.wmnet"
    sudo -u librenms ./lnms device:add --v2c -c $COMMUNITY $line.mgmt.$SITE.wmnet
    sudo -u librenms php discovery.php -h $line.mgmt.$SITE.wmnet && sudo -u librenms php poller.php -h $line.mgmt.$SITE.wmnet
done < $1
