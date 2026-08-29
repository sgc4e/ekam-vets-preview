#!/bin/bash
# Run this AFTER ekamvets.com is added in Hostinger hPanel and DNS points at Hostinger.
# It moves the already-staged files into place and verifies.
set -e
HOST=u716426288@145.79.210.56; PORT=65002; KEY=~/.ssh/wearec4e_hostinger
ssh -i $KEY -p $PORT $HOST 'set -e
  test -d domains/ekamvets.com/public_html || { echo "STOP: add ekamvets.com in hPanel first"; exit 1; }
  cp -a ekamvets-staging/. domains/ekamvets.com/public_html/
  echo "copied $(find domains/ekamvets.com/public_html -type f | wc -l) files"'
echo "--- live check ---"
for p in "" hi/ blog.html rates.html visit.html sitemap.xml robots.txt nope-404-test; do
  printf "%-16s %s\n" "/$p" "$(curl -s -o /dev/null -w '%{http_code}' https://ekamvets.com/$p)"
done
