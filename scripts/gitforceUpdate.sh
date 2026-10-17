#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo "running fetch"
git fetch

echo "updating all files"
git reset --hard origin/main

echo "cleaning old files"
git clean -fd

echo "omg its done"

