#!/bin/bash

set -e

MOUNTPOINT=$1

echo "mountpoint" MOUNTPOINT

exec /usr/bin/umount MOUNTPOINT

echo gay!
