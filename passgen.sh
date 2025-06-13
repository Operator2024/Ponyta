#!/usr/bin/env bash
set -Eeuo pipefail

echo "Run htpasswd generator..."
htpasswd_string=$(htpasswd -nBC 12 "" | tr -d ':\n')

echo "Encrypted password=$htpasswd_string"
