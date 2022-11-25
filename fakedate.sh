#!/bin/bash
# Helper file to fake system date on a debian system to use expired license
set -x
sudo systemctl stop systemd-timesyncd.service
NOWTIME=$(date "+%T")
date -s "1 JUN 2021 $NOWTIME"
hwclock -w
