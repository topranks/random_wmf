#!/bin/bash
get_ifindex () {
    RESULT=""
    INTERFACES=$(snmpwalk -v2c -c $COMMUNITY $1 IF-MIB::ifDescr)
    while IFS= read -r line
    do
        INT_NAME=$(echo "$line" | awk '{print $NF}')
        if [ "$INT_NAME" = "$2" ]; then
            RESULT=$(echo "$line" | awk '{print $1}' | awk -F"." '{print $NF}')
            break
        fi
    done <<< "$INTERFACES"
    echo "$RESULT"
}

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <router1> <int1> <router2> <int2>"
    exit 1
fi

R1=$1
R1_INT=$2
R2=$3
R2_INT=$4

echo -n "Community String: "
read -s COMMUNITY
echo -e "\n"

R1_IDX=$(get_ifindex $R1 $R1_INT)
R2_IDX=$(get_ifindex $R2 $R2_INT)

echo "Time,$R1 $R1_INT Out,$R2 $R2_INT In"
while true;
do
    date +"%T" | tr '\n' ','
    snmpget -Oqv -v2c -c $COMMUNITY $R1 1.3.6.1.2.1.31.1.1.1.11.$R1_IDX | tr '\n' ','
    snmpget -Oqv -v2c -c $COMMUNITY $R2 1.3.6.1.2.1.31.1.1.1.7.$R2_IDX | tr '\n' ','
    echo ""
    sleep 10
done

