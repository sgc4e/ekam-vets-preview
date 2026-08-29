# ekam vets — handoff for Claude Code

Website for an integrated veterinary clinic in Vidyadhar Nagar, Jaipur. Static HTML,
two languages, deployed to Hostinger. Built 29 Aug 2026 in a Cowork session.

**Read this whole file before touching anything.** Several things here look editable
and are not, and several obvious approaches have already been tried and failed.

---

## 1. Where things are

| What | Where |
|---|---|
| Source of truth | `/Users/sg/Documents/Claude/Projects/ekam-vets-site` |
| Git remote | `github.com/sgc4e/ekam-vets-preview` (public) |
| Preview site | https://sgc4e.github.io/ekam-vets-preview/ (stays `noindex`) |
| Production | https://ekamvets.com |
| Local dev | `python3 -m http.server 4321` in the repo root |
| Host | Hostinger Business plan, expires 2027-04-11 |
| SSH | `ssh -i ~/.ssh/wearec4e_hostinger -p 65002 u716426288@145.79.210.56` |
| Webroot | `domains/ekamvets.com/public_html` |

Project notes live in the claude.ai Project "Ashi Pet Clinic Aug 2026":
`ashi-brand-brief`, `ashi-design-guide`, `ashi-decisions-open-loops`,
`ashi-competition-map`, `ashi-website-v1`, `ashi-website-hindi`,
`ashi-website-services-and-blog`, `ashi-website-golive`.

---

## 2. Repo layout

```
*.html              17 English pages (source of truth, edit these)
hi/*.html           17 Hindi pages (GENERATED — never edit by hand)
style.css           single stylesheet, appended to in versioned blocks
send.php            booking form handler
img/                logo files + 12 unused SVG panels
_hi1..._hi8.json    English→Hindi dictionary, 771 entries
_gen_hi.py          generates hi/ from the English pages
build.py            produces dist/ for a real domain
deploy.sh           build + rsync to Hostinger
go-live.sh          one-off: copy staged files into the vhost
mail-config.sample.php  template for SMTP creds (real one lives on the server)
```

Pages: `index` `integrated-care` `services` `rates` `community` `about` `faq`
`visit` `thanks` `blog` and seven `blog-*.html`.

---

## 3. The two build steps, in order

```bash
# 1. after ANY English edit, regenerate Hindi
python3 _gen_hi.py            # prints untranslated count, writes _missing.txt

# 2. post-process Hindi (rupee symbol + cache-buster) — see §4
# 3. deploy
./deploy.sh ekamvets.com                # live and indexable
./deploy.sh ekamvets.com --noindex      # live but hidden from search
```

`build.py` adds, on top of the source: absolute canonical, hreflang en-IN/hi-IN/x-default,
Open Graph with `og:locale`, `VeterinaryCare` JSON-LD on the home page, `sitemap.xml`
(32 URLs, thanks pages excluded), open `robots.txt`, a branded `404.html`, and `.htaccess`
(HTTPS + non-www redirect, gzip, cache headers, security headers). It strips the `noindex`
meta the source carries, except on `thanks.html`.

---

## 4. The Hindi pipeline — read this before editing anything

**`hi/` is generated. Editing it is wasted work; the next run overwrites it.**

To change Hindi copy, change the dictionary. To change English copy, edit the English
page, then re-run the generator and add any new strings to `_hi8.json`.

The generator prints `untranslated unique strings: N` and writes them to `_missing.txt`.
**That number must be 0 before deploying.** A non-zero count means English text will
appear on a Hindi page.

After every `_gen_hi.py` run, apply the post-processing it does not do:

```bash
python3 - <<'PY'
import glob,re
for f in glob.glob('hi/*.html'):
    s=open(f,encoding='utf-8').read()
    s=re.sub(r'\bRs (\d)', r'₹\1', s).replace('Rs 400','₹400').replace('Rs 900','₹900')
    s=re.sub(r'href="\.\./style\.css[^"]*"','href="../style.css?v=17"',s)
    open(f,'w',encoding='utf-8').write(s)
for f in glob.glob('*.html'):
    s=open(f,encoding='utf-8').read()
    open(f,'w',encoding='utf-8').write(re.sub(r'href="style\.css[^"]*"','href="style.css?v=17"',s))
PY
```

Bump the `v=` number whenever `style.css` changes. Chrome serves stale CSS otherwise;
this cost real debugging time. Current version is **v16**, so the next edit uses v17.

---

## 5. Gotchas that already bit, in the order they will bite again

1. **`write_file` corrupts `.svg`.** Desktop Commander treats the extension as binary and
   writes a few bytes of garbage while reporting success. Write SVGs with a quoted heredoc
   through `start_process` instead. HTML and CSS are fine.

2. **The generator's pass-through filter must run AFTER the dictionary lookup.** There is a
   rule that leaves number-and-short-word strings alone so prices survive. It originally ran
   first and silently left `"8.7 by 10 ft"`, `"9.3 by 8 ft"` and `"IPD"` in English on the
   Hindi About page, without reporting them as missing. If short strings turn up untranslated,
   that ordering is the bug.

3. **`.htaccess` percent signs.** The block in `build.py` is a plain string, not `%`-formatted.
   Write `%{HTTPS}` and `%1`, not `%%{HTTPS}` and `%%1`. Shipped once as
   `https://%%ekamvets.com%/` and every redirect was broken. Verify with:
   `curl -s -D- -o /dev/null -H 'Host: ekamvets.com' http://145.79.210.56/rates.html | grep -i location`

4. **A `200` from `https://ekamvets.com/` does not mean the site is up.** Hostinger's CDN
   serves a lander that also returns 200. Check the body, not the status code.

5. **This account's Hostinger nameservers are `atlas.dns-parking.com` and
   `hyperion.dns-parking.com`**, not the generic `ns1`/`ns2.dns-parking.com`. The generic pair
   was set first and did not work. Always read the pair hPanel names.

6. **`dig` on SG's Mac uses a local cached resolver** and lied about propagation for an hour.
   Query a public resolver explicitly: `dig +short NS ekamvets.com @8.8.8.8`.

7. **PHP `mail()` is disabled on this account** — the server returns
   `550 Local sendmail disabled for u716426288`. Do not write anything that calls `mail()`.
   See §6.

8. **The ekamvets.com dashboard in hPanel does not load.** The Dashboard button greys out and
   the SPA never routes, so Security → SSL is unreachable by URL or menu. If SSL needs
   installing, SG has to do it from his own browser session.


9. **Image files can upload as mode 600 and 403 on the web.** Files brought over from the Mac
   via the device bridge arrive `-rw-------`, rsync preserves that, and Apache then refuses
   them. The logo and favicon 403'd on the live site this way while every HTML page returned
   200. `deploy.sh` now passes `--chmod=D755,F644`. If an asset 404s or 403s, check
   permissions before you check paths.

---

## 6. The booking form

`visit.html` and `hi/visit.html` POST to `/send.php`. Honeypot field named `website`.
Missing name or phone redirects back with `?e=1`. Success goes to `/thanks.html` or
`/hi/thanks.html`, both `noindex` and out of the sitemap. The Hindi form carries
`name="lang" value="hi"`, set by the generator.

Because `mail()` is disabled, `send.php` does two things:

1. **Appends every submission to `~/domains/ekamvets.com/form-log.txt`**, outside the webroot.
   This runs first, so no enquiry is lost regardless of mail.
2. **Sends over SMTP** to `smtp.hostinger.com:465` using credentials from
   `~/domains/ekamvets.com/mail-config.php`, also outside the webroot.

**`mail-config.php` does not exist yet.** `mail-config.sample.php` sits beside where it goes.
SG has to create it with the `hello@ekamvets.com` mailbox password. Claude does not handle
passwords. Until then, submissions are logged but not emailed. Check the log with:

```bash
ssh -i ~/.ssh/wearec4e_hostinger -p 65002 u716426288@145.79.210.56 \
  'tail -40 domains/ekamvets.com/form-log.txt'
```

A WhatsApp button (`wa.me/919082053255`, prefilled) sits beside the submit button as the
channel that needs no configuration.

---

## 7. Email

- Free Business Email plan on ekamvets.com. Mailbox `hello@ekamvets.com`.
- Forwarder `hello@ekamvets.com` → `drashima@gmail.com`, active. The free plan allows one.
- Catch-all `*@ekamvets.com` → `hello@ekamvets.com`, **status: waiting confirmation**.
  Hostinger emailed a link to hello@, which forwards to Gmail. Dr Ashima clicks it once.
- DNS zone already has MX (mx1/mx2.hostinger.com), SPF, three DKIM CNAMEs and DMARC.

---

## 8. Content rules that are not style preferences

These come from `ashi-design-guide` and `ashi-decisions-open-loops`. Breaking them has
legal or commercial consequences, not aesthetic ones.

- **Brand is lower case. Always.** `ekam vets`, never `Ekam Vets`, including at the start of a
  sentence and in `<title>`. Same for the Sanskrit word in running copy: "ekam means one".
- **No doctor names anywhere.** One founder is a government employee whose name cannot be on
  paper. The clinic runs under a hospital name and the About page says so deliberately.
- **Homeopathy is on the site by SG's explicit instruction, reversing the guide's ban.** Every
  mention must state it is prescribed *inside the veterinary consult, by a registered
  veterinary surgeon*, alongside medicine and never instead of it. The paragraph naming where
  it is never used — infection, trauma, poisoning, dehydration, pain, parvovirus, heat stroke,
  blocked bladder — is the legal shield. Do not soften or remove it.
- **No "India's first integrated practice"** or any unverified first-mover claim.
- **No anti-breeder stance on the site.** Internal position only.
- **No Hindi on the English pages.** Removed on instruction, three separate times. The Hindi
  site carries that register instead.
- **Rate card prices are indicative and mostly fabricated.** Only consult 350, grooming 1000
  and physio 500 came from the founders, and even those were off-tape. The page carries an
  explicit "indicative, confirmed at reception" line. Do not remove it while the numbers are
  unconfirmed. Open loops 1 and 4 in `ashi-decisions-open-loops`.
- **Voice:** short sentences, no em dashes, no adverb padding, no exclamation marks, no emoji.

---

## 9. Current state and what is left

Deployed and correct on the server: 35 HTML pages, style.css, send.php, img/, sitemap,
robots.txt, 404, .htaccess.

Open, in rough priority order:

1. **SSL not issued.** ekamvets.com still serves Hostinger's parking lander and HTTPS fails
   certificate verification. DNS and the DNS zone are correct; this is Hostinger provisioning.
   Needs the hPanel dashboard, which will not load for Claude. Verify with:
   `curl -s -m 20 http://ekamvets.com/ | head -c 120` — if it mentions `/lander`, still pending.
2. **`mail-config.php`** with the mailbox password, so the form actually emails.
3. **Catch-all confirmation** click by Dr Ashima.
4. **Every photograph is Unsplash stock**, hotlinked from their CDN, on the clinic's own domain.
   The design guide bans stock outright and asks for real animals from the catchment with hands
   in frame. This is the biggest remaining quality gap.
5. **Google Search Console** — verify, submit `https://ekamvets.com/sitemap.xml`.
6. **Google Business Profile** with the same name, phone and address. For a neighbourhood
   clinic this outranks the website for "vet near me".
7. **Logo vs wordmark mismatch.** The supplied logo is a geometric lowercase sans; the site sets
   the wordmark in Frank Ruhl Libre, a serif. Lowercasing made it visible. Undecided.
8. **The design guide disqualifies the paw print** used in the logo. SG chose it anyway. On
   record, not relitigated.

---

## 10. Facts

- Phone / WhatsApp / emergency: **+91 90820 53255**
- Address: **Sector 1, Vidyadhar Nagar, Jaipur 302039**
- Email: hello@ekamvets.com
- Hours: Mon–Sat 9am–8pm, Sun 10am–2pm
- Consult: Rs 350, one free follow-up within seven days
- Clinic: ~55 × 29.24 ft ground floor, step free. Reception, waiting area, two consulting
  rooms, two treatment rooms (second doubles as OT), dedicated OT, IPD beds, rooms 5 and 8,
  kitchen, washroom, staff room, small temple.
- Nine services: wellness exams, physiotherapy, in-house lab, surgery/OT/IPD, grooming,
  homeopathy, herbal medicine, massage and acupuncture, senior and palliative care.
