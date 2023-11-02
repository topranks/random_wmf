#!/usr/bin/env python3

# Icinga check for down IBGP sessions

# Requires the MIBs: mib-jnx-bfd-exp, mib-jnx-exp, mib-jnx-smi
# Returns CRITICAL if the number of configured IBGP peerings doesn't match
# number in ESTABLISHED state.
#
# Usage:
# python3 check_ibgp --host HOSTNAME --community COMMUNITY
#
# cmooney@wikimedia.org

import argparse
import sys

from snimpy.manager import Manager
from snimpy.manager import load
from snimpy.snmp import SNMPException

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", nargs=1, dest='host', required=True, help="Target hostname")
    parser.add_argument("--community", nargs=1,
                        dest='community', required=True, help="SNMP community")
    options = parser.parse_args()

    load("BGP4-MIB")
    snimpyManager = Manager(options.host[0], options.community[0], 2, cache=True)

    try:
        local_as = snimpyManager.bgpLocalAs
    except SNMPException as e:
        print(f"SNMP exception polling device - {e}")
        sys.exit(3)

    # Get indexes of IBGP peers by comparing the peer ASNs
    ibgp_peer_idx = []
    for index, peer_as in snimpyManager.bgpPeerRemoteAs.items():
        if peer_as == local_as:
            ibgp_peer_idx.append(index)

    # Remove any in admin down state 
    for index, admin_state in snimpyManager.bgpPeerAdminStatus.items():
        if index in ibgp_peer_idx and admin_state != 2:
            ibgp_peer_idx.remove(index)

    # Count any that don't return 6 (established) for peerState
    down_peers = 0
    for index, peer_state in snimpyManager.bgpPeerState.items():
        if index in ibgp_peer_idx and peer_state != 6:
            down_peers += 1

    return_code = 0
    if down_peers > 0:
        return_code = 2
    print(f"{len(ibgp_peer_idx)-down_peers}/{len(ibgp_peer_idx)} IBGP peers in established state.")
    sys.exit(return_code)


if __name__ == "__main__":
    main()
