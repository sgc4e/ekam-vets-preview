#!/bin/bash
# Deploy ekam vets to Hostinger.
#   ./deploy.sh ekamvets.in            -> live and indexable
#   ./deploy.sh ekamvets.in --noindex  -> live but hidden from search
set -e
DOMAIN="$1"; shift || true
[ -z "$DOMAIN" ] && { echo "usage: ./deploy.sh <domain> [--noindex]"; exit 1; }
HOST=u716426288@145.79.210.56
PORT=65002
KEY=~/.ssh/wearec4e_hostinger
REMOTE="domains/$DOMAIN/public_html/"

python3 build.py "$DOMAIN" "$@"
echo "--- checking remote path ---"
ssh -i $KEY -p $PORT $HOST "test -d $REMOTE && echo 'remote ok: $REMOTE' || { echo 'MISSING: add $DOMAIN in hPanel first'; exit 1; }"
echo "--- uploading ---"
rsync -az --delete -e "ssh -i $KEY -p $PORT" dist/ "$HOST:$REMOTE"
echo "--- live ---"
for p in "" hi/ blog.html rates.html sitemap.xml robots.txt; do
  printf "%-16s %s\n" "/$p" "$(curl -s -o /dev/null -w '%{http_code}' https://$DOMAIN/$p)"
done
