import re, glob, json, os, sys

D = {}
for p in sorted(glob.glob('_hi*.json')):
    D.update(json.load(open(p, encoding='utf-8')))

SKIP = re.compile(r'^(&nbsp;|[\s&;·×"“”]*)$')
def keep_asis(t):
    # numbers, prices, measurements, brand, emails, symbols pass through
    return bool(re.fullmatch(r'[0-9\s.,%×&;·:/+\-–—()a-zA-Z]*', t)) and not re.search(r'[a-zA-Z]{4,}', t)

os.makedirs('hi', exist_ok=True)
missing = []

for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()

    # --- English page: add the switcher ---
    if 'class="lang"' not in s:
        s = s.replace('<a href="visit.html" class="cta',
                      '<a class="lang" href="hi/%s">हिंदी</a>\n      <a href="visit.html" class="cta' % f, 1)
        open(f, 'w', encoding='utf-8').write(s)

    h = s
    # --- translate ---
    def tr_text(m):
        raw = m.group(1); t = raw.strip()
        if t in D: return '>' + raw.replace(t, D[t]) + '<'
        if SKIP.match(t) or keep_asis(t): return m.group(0)
        missing.append((f, t)); return m.group(0)

    parts = h.split('<body>')
    head, body = (parts[0], parts[1]) if len(parts) > 1 else ('', h)
    body = re.sub(r'>([^<>]+)<', tr_text, body)

    for attr in ('alt', 'placeholder'):
        def tr_attr(m, a=attr):
            t = m.group(1).strip()
            if t in D: return '%s="%s"' % (a, D[t])
            if not t or keep_asis(t): return m.group(0)
            missing.append((f, t)); return m.group(0)
        body = re.sub(attr + r'="([^"]*)"', tr_attr, body)

    def tr_head(m, tag):
        t = m.group(1).strip()
        if t in D: return m.group(0).replace(t, D[t])
        missing.append((f, t)); return m.group(0)
    head = re.sub(r'<title>([^<]+)</title>', lambda m: tr_head(m, 'title'), head)
    head = re.sub(r'(?<=name="description" content=")([^"]+)', lambda m: tr_head(m, 'desc'), head)

    h = head + '<body>' + body
    # --- paths + lang ---
    h = h.replace('<html lang="en">', '<html lang="hi">')
    h = re.sub(r'href="style\.css([^"]*)"', r'href="../style.css\1"', h)
    h = h.replace('href="img/', 'href="../img/').replace('src="img/', 'src="../img/')
    h = re.sub(r'<a class="lang" href="[^"]*">[^<]*</a>', '<a class="lang" href="../%s">English</a>' % f, h)
    h = re.sub(r'hreflang="en" href="[^"]*"', 'hreflang="en" href="../%s"' % f, h)
    h = re.sub(r'hreflang="hi" href="[^"]*"', 'hreflang="hi" href="%s"' % f, h)
    open('hi/' + f, 'w', encoding='utf-8').write(h)

seen = set(); out = []
for f, t in missing:
    if t not in seen: seen.add(t); out.append(t)
open('_missing.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('pages written:', len(glob.glob('hi/*.html')))
print('dictionary:', len(D), 'entries')
print('untranslated unique strings:', len(out))
