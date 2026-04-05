#!/bin/sh

# Fix permissions as root
mkdir -p /appuser/uploads
chown -R appuser:appgroup /appuser/uploads

exec gosu appuser "$@"