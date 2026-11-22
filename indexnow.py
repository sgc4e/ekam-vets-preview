#!/usr/bin/env python3
"""Ping IndexNow with the URLs whose lastmod changed in this deploy.

  python3 indexnow.py <domain> <old-sitemap.xml>

deploy.sh saves the live sitemap before uploading, then calls this after. Any URL
that is new, or whose <lastmod> differs from the old copy, is sent. One POST
reaches Bing, Yandex, Naver, Seznam and Yep. Google does not take part.
"""
import glob, json, re, sys, urllib.request, urllib.error

def entries(xml):
    return dict(re.findall(r'<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', xml))

def changed(old_xml, new_xml):
    old = entries(old_xml)
    return [u for u, m in entries(new_xml).items() if old.get(u) != m]

if __name__ == '__main__':
    assert changed('<loc>a</loc><lastmod>1</lastmod><loc>b</loc><lastmod>1</lastmod>',
                   '<loc>a</loc><lastmod>1</lastmod><loc>b</loc><lastmod>2</lastmod>'
                   '<loc>c</loc><lastmod>1</lastmod>') == ['b', 'c']
    domain, old_path = sys.argv[1], sys.argv[2]
    key = next(f[:-4] for f in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', f))
    try:
        old_xml = open(old_path, encoding='utf-8').read()
    except OSError:
        old_xml = ''
    urls = changed(old_xml, open('dist/sitemap.xml', encoding='utf-8').read())
    if not urls:
        print('IndexNow: no changed URLs'); sys.exit(0)
    body = json.dumps({'host': domain, 'key': key,
                       'keyLocation': 'https://%s/%s.txt' % (domain, key),
                       'urlList': urls}).encode()
    # api.indexnow.org relays Bing's answer. Bing has refused this host since Nov 2026
    # (403 UserForbiddedToAccessSite) while Yandex accepts the same key, so try Yandex too.
    ok = False
    for ep in ('https://api.indexnow.org/indexnow', 'https://yandex.com/indexnow'):
        req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print('IndexNow %s %s: %d URLs submitted' % (ep, r.status, len(urls))); ok = True
        except urllib.error.HTTPError as e:
            print('IndexNow %s %s: %s' % (ep, e.code, e.read()[:160].decode('utf-8', 'replace')))
    sys.exit(0 if ok else 1)
