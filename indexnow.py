#!/usr/bin/env python3
"""Ping IndexNow with the URLs whose lastmod changed in this deploy.

  python3 indexnow.py <domain> <old-sitemap.xml>

deploy.sh saves the live sitemap before uploading, then calls this after. Any URL
that is new, or whose <lastmod> differs from the old copy, is sent. One POST
reaches Bing, Yandex, Naver, Seznam and Yep. Google does not take part.
"""
import glob, json, re, sys, urllib.request

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
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req) as r:
        print('IndexNow %s: %d URLs submitted' % (r.status, len(urls)))
