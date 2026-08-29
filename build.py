#!/usr/bin/env python3
"""Build a deployable, indexable copy of the site into dist/ for a real domain.

  python3 build.py ekamvets.in            # indexable (default)
  python3 build.py ekamvets.in --noindex  # keep search engines out
"""
import sys, os, re, glob, shutil, datetime

if len(sys.argv) < 2:
    sys.exit('usage: python3 build.py <domain> [--noindex]')
DOMAIN = sys.argv[1].strip().lower().lstrip('.')
NOINDEX = '--noindex' in sys.argv
BASE = 'https://' + DOMAIN
TODAY = datetime.date.today().isoformat()

if os.path.isdir('dist'): shutil.rmtree('dist')
os.makedirs('dist/hi', exist_ok=True)
os.makedirs('dist/img', exist_ok=True)
for f in glob.glob('img/*'): shutil.copy2(f, 'dist/img/')
shutil.copy2('style.css', 'dist/style.css')

SCHEMA = """<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"VeterinaryCare",
  "name":"ekam vets",
  "description":"Integrated holistic veterinary clinic in Vidyadhar Nagar, Jaipur. Medicine, physiotherapy, homeopathy, herbal medicine, in-house lab, operation theatre and in-patient beds under one roof.",
  "url":"%(base)s/",
  "logo":"%(base)s/img/logo.png",
  "image":"%(base)s/img/logo.png",
  "telephone":"+919082053255",
  "priceRange":"Rs 350 onwards",
  "currenciesAccepted":"INR",
  "paymentAccepted":"Cash, UPI, Card",
  "address":{"@type":"PostalAddress","streetAddress":"Sector 1, Vidyadhar Nagar","addressLocality":"Jaipur","addressRegion":"Rajasthan","postalCode":"302039","addressCountry":"IN"},
  "areaServed":[{"@type":"Place","name":"Vidyadhar Nagar"},{"@type":"Place","name":"Shastri Nagar"},{"@type":"Place","name":"Jhotwara"},{"@type":"Place","name":"Jaipur"}],
  "openingHoursSpecification":[
    {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"09:00","closes":"20:00"},
    {"@type":"OpeningHoursSpecification","dayOfWeek":"Sunday","opens":"10:00","closes":"14:00"}
  ],
  "availableService":[
    {"@type":"MedicalProcedure","name":"Veterinary consultation"},
    {"@type":"MedicalProcedure","name":"Animal physiotherapy"},
    {"@type":"MedicalProcedure","name":"Homeopathy prescribed by a registered veterinary surgeon"},
    {"@type":"MedicalProcedure","name":"Herbal and natural medicine"},
    {"@type":"MedicalProcedure","name":"Massage and acupuncture"},
    {"@type":"MedicalProcedure","name":"Senior and palliative care"},
    {"@type":"MedicalProcedure","name":"In-house laboratory and imaging"},
    {"@type":"MedicalProcedure","name":"Surgery and in-patient care"},
    {"@type":"MedicalProcedure","name":"Grooming"}
  ]
}
</script>
""" % {'base': BASE}

def title_of(s):
    m = re.search(r'<title>([^<]*)</title>', s); return m.group(1) if m else 'ekam vets'
def desc_of(s):
    m = re.search(r'name="description" content="([^"]*)"', s); return m.group(1) if m else ''

pages = []
for src in sorted(glob.glob('*.html')) + sorted(glob.glob('hi/*.html')):
    if os.path.basename(src).startswith('_'): continue
    s = open(src, encoding='utf-8').read()
    hi = src.startswith('hi/')
    name = os.path.basename(src)
    url = '%s/hi/%s' % (BASE, name) if hi else '%s/%s' % (BASE, name)
    if name == 'index.html': url = url[:-len('index.html')]

    # robots
    if NOINDEX:
        s = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex, nofollow">', s)
    else:
        s = re.sub(r'\s*<meta name="robots"[^>]*>', '', s)

    # absolute hreflang + x-default + canonical
    s = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
    alts = ('<link rel="canonical" href="%s">\n'
            '<link rel="alternate" hreflang="en-IN" href="%s/%s">\n'
            '<link rel="alternate" hreflang="hi-IN" href="%s/hi/%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s/%s">\n'
            ) % (url, BASE, name if name!='index.html' else '', BASE, name if name!='index.html' else '', BASE, name if name!='index.html' else '')
    og = ('<meta property="og:type" content="website">\n'
          '<meta property="og:site_name" content="ekam vets">\n'
          '<meta property="og:title" content="%s">\n'
          '<meta property="og:description" content="%s">\n'
          '<meta property="og:url" content="%s">\n'
          '<meta property="og:image" content="%s/img/logo.png">\n'
          '<meta property="og:locale" content="%s">\n'
          '<meta name="twitter:card" content="summary_large_image">\n'
          ) % (title_of(s), desc_of(s).replace('"','&quot;'), url, BASE, 'hi_IN' if hi else 'en_IN')
    inject = alts + og + (SCHEMA if name == 'index.html' else '')
    s = s.replace('<link rel="icon"', inject + '<link rel="icon"', 1)

    # relative asset paths stay correct; write out
    out = 'dist/hi/' + name if hi else 'dist/' + name
    open(out, 'w', encoding='utf-8').write(s)
    pages.append((url, name, hi))

# sitemap with hreflang pairs
rows = []
for url, name, hi in pages:
    if hi: continue
    en = '%s/%s' % (BASE, '' if name == 'index.html' else name)
    hin = '%s/hi/%s' % (BASE, '' if name == 'index.html' else name)
    rows.append("""  <url>
    <loc>%s</loc>
    <lastmod>%s</lastmod>
    <xhtml:link rel="alternate" hreflang="en-IN" href="%s"/>
    <xhtml:link rel="alternate" hreflang="hi-IN" href="%s"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>
  </url>
  <url>
    <loc>%s</loc>
    <lastmod>%s</lastmod>
    <xhtml:link rel="alternate" hreflang="en-IN" href="%s"/>
    <xhtml:link rel="alternate" hreflang="hi-IN" href="%s"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>
  </url>""" % (en, TODAY, en, hin, en, hin, TODAY, en, hin, en))
open('dist/sitemap.xml','w',encoding='utf-8').write(
 '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
 + '\n'.join(rows) + '\n</urlset>\n')

open('dist/robots.txt','w',encoding='utf-8').write(
 'User-agent: *\nDisallow: /\n' if NOINDEX else
 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE)

# 404
idx = open('dist/index.html', encoding='utf-8').read()
head = idx.split('<body>')[0]
header = idx.split('<body>')[1].split('</header>')[0] + '</header>'
footer = '<footer class="site">' + idx.split('<footer class="site">')[1]
head = re.sub(r'<title>[^<]*</title>', '<title>Page not found · ekam vets</title>', head)
open('dist/404.html','w',encoding='utf-8').write(head + '<body>\n' + header + """
<div class="pagehead"><div class="wrap narrow">
  <p class="eyebrow">404</p>
  <h1>That page is not here.</h1>
  <p>The link may be old, or we may have moved it. The clinic is still open.</p>
</div></div>
<section><div class="wrap narrow" style="text-align:center">
  <p><a class="btn dark" href="/">Go to the home page</a> &nbsp; <a class="btn line" href="/visit.html">Book a visit</a></p>
</div></section>
""" + footer)

open('dist/.htaccess','w',encoding='utf-8').write("""# ekam vets
RewriteEngine On
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} ^www\\. [NC]
RewriteCond %{HTTP_HOST} ^(?:www\\.)?(.+)$ [NC]
RewriteRule ^ https://%1%{REQUEST_URI} [L,NE,R=301]

ErrorDocument 404 /404.html
DirectoryIndex index.html

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css text/xml application/javascript image/svg+xml
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/css "access plus 7 days"
ExpiresByType image/png "access plus 30 days"
ExpiresByType image/svg+xml "access plus 30 days"
ExpiresByType text/html "access plus 1 hour"
</IfModule>
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
""")

n_html = len(glob.glob('dist/*.html')) + len(glob.glob('dist/hi/*.html'))
print('domain      :', DOMAIN)
print('indexable   :', 'NO (noindex kept)' if NOINDEX else 'YES')
print('html pages  :', n_html)
print('sitemap urls:', len(rows)*2)
print('dist/ ready')
