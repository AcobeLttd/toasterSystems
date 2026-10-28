#!/bin/bash

set -e

DEVICE=$1
MOUNTPOINT=$2

echo "device" $DEVICE

echo "mountpoint" $MOUNTPOINT

exec /usr/bin/mount $DEVICE $MOUNTPOINT

echo gay!
