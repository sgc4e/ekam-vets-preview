# ekam vets site: tasks

## Next time: remind SG first (set 22 Nov 2026)

- [ ] SG: verify Search Console (Domain property, TXT record in Hostinger DNS), submit https://ekamvets.com/sitemap.xml, create GA4
- [ ] SG: add the site to Bing Webmaster Tools (import from Search Console) and check whether Bingbot is blocked; if so, raise it with Hostinger. Also ask Hostinger why GPTBot gets 429
- [ ] Clinic: create the Google Business Profile with exactly: ekam vets · 134, Sector 1, Vidyadhar Nagar, Jaipur 302039 · +91 91659 31975 · Mon to Sat 9am to 8pm, Sun 10am to 2pm. Then swap the map link and hasMap to the profile pin
- [ ] Clinic: confirm prices in writing (E22), then fix the vet-cost post's prices, remove it from HIDDEN in build.py and fill the rate card
- [ ] Clinic: real photos, then drop the "Placeholder photography" footer line (E6)
- [ ] Native Hindi check of the 10 new strings in _hi10.json
- [ ] Mirror the 22 Nov SEO changes into the WordPress port (wp/) before cutover

## Done

- [x] Build English preview site, 17 pages (2026-08-29)
- [x] Remove Hindi copy from English pages (2026-08-29)
- [x] Add Hindi site under /hi with language switch, dictionary-driven generator (2026-08-29)
- [x] Fix untranslated strings on Hindi pages (2026-08-29)
- [x] Add homeopathy, herbal, bodywork, senior care; 7-post blog; translate all (2026-08-29)
- [x] Fix language switcher targets on blog pages (2026-08-29)
- [x] Hostinger build + deploy pipeline: canonical, hreflang, OG, JSON-LD, sitemap, 404, htaccess (2026-08-29)
- [x] Real phone and address, indicative pricing note (2026-08-29)
- [x] Fix htaccess redirect, deploy to ekamvets.com (2026-08-29)
- [x] Booking form: send.php with SMTP + log fallback, thanks pages, WhatsApp button (2026-08-29)
- [x] CLAUDE.md handoff (2026-08-29)
- [x] Fix 403 on images, deploy forces 644/755 (2026-08-29)
- [x] Remove building section from About, tame for-profit copy, fix header logo (2026-08-29)
- [x] SSL live on ekamvets.com, verified over HTTPS (2026-09-22)

## Open

- [ ] mail-config.php with hello@ mailbox password (SG)
- [ ] Catch-all forwarder confirmation click (Dr Ashima)
- [ ] Replace Unsplash stock with real clinic photos
- [ ] Google Search Console: verify, submit sitemap
- [ ] Google Business Profile
- [ ] Decide logo vs wordmark typeface mismatch
- [x] Pick a CMS for a non-technical editor: WordPress, both languages (SG, 2026-09-22)
- [~] CloudCannon: dropped, $49-55/mo, no Python builds, editors cannot add sections
- [ ] Choose Hindi plugin (machine draft into Hindi + review before publish) — compared WPML/Polylang/TranslatePress/Weglot/GTranslate/MultilingualPress/Linguise 2026-09-22, all-in research in chat; recommendation Polylang Pro (€99/yr, DeepL, draft-then-publish gate), WPML runner-up. Decision still SG's.
- [ ] Block theme from style.css: theme.json, header/footer/tabbar parts, templates
- [ ] Convert 17 English pages into native blocks
- [ ] Hindi pages into WordPress, linked to English
- [ ] Staging WordPress on Hostinger (SG installs, Claude configures over WP-CLI)
- [ ] Editor guardrails: lock homeopathy shield and indicative-price line
- [ ] Booking form, SEO (hreflang, schema, sitemap), .html to new URL redirects
- [ ] Side-by-side visual check against the static site, both languages
- [ ] Cutover: WordPress replaces static on ekamvets.com

## SEO / AEO fixes from the 23 Oct 2026 audit

- [x] IndexNow key file at the site root + ping changed URLs in deploy.sh — 2026-10-23
- [x] Sitemap lastmod from git history per file, not the build date — 2026-10-23
- [x] HSTS header in .htaccess — 2026-10-23
- [x] "How did you hear about us?" in the booking form and send.php — 2026-10-23
- [x] README.md: drop stale "preview, placeholders, noindex" — 2026-10-23
- [~] GA4 — skipped: no measurement ID in repo or master.env; SG to create the property
- [x] Deployed live (2c5fb64), IndexNow 202 for 30 URLs — 2026-10-23
- [x] Phone number changed to +91 91659 31975 everywhere (70 occurrences, 42 files: EN + HI pages, _hi8.json dictionary, JSON-LD, WhatsApp links, wp/ migration content) and deployed live — 2026-11-03
- [x] Tagline "Integrated holistic vets" to "Compassionate holistic care" on all EN/HI pages, WP source too (2026-11-07)
- [x] Location: "Get directions" Google Maps link in every footer, map embed + "Open in Google Maps" on Visit, hasMap in JSON-LD (2026-11-07)
- [ ] Swap the address-search map link for the Google Business Profile pin once the profile exists
- [x] Deploy tagline + location changes live (2026-11-07)

- [ ] SEO-Desk intake 21 Nov 2026: run new checks D17 (retitle low-CTR pages), D18 (links from click-earning pages), D19 (hub pages), E27 (vs pages only on demand), I10 (translate by language demand) and sharpened D4, E3, L6, L7 from SEO-Desk/knowledge/SEO-CHECKLIST.md

## SEO pass 22 Nov 2026 (deployed live 22 Nov, 95c3e60)

- [x] E2: "veterinary clinic" in home title, H1 sub-line and first sentence, EN + HI — 2026-11-22
- [x] E3: phone is a tel:+919165931975 link everywhere it appears (22 places, EN; HI regenerated) — 2026-11-22
- [x] E5: blog read-on links from services (limping, tick fever, homeopathy), FAQ + rates (vaccination), visit (heat stroke), community (street dog first aid) — 2026-11-22
- [x] E4: vet-cost card back in blog.html; build.py strips it while the post is in HIDDEN. Post stays hidden: its prices are unconfirmed — 2026-11-22
- [x] E1 prep: build.py injects google-site-verification on the home page when GSC_VERIFICATION is set — 2026-11-22
- [x] style.css v20 (h1 sub-line, read-on links, tel links) — 2026-11-22
- [ ] E6: remove "Placeholder photography from Unsplash" footer line once real clinic photos are in img/ (none yet)
- [ ] E22: clinic confirms prices in writing, then fix blog-vet-cost-jaipur.html prices, un-hide it, fill the rate card
- [ ] E1: SG verifies Search Console (DNS TXT or HTML tag), submits sitemap, creates GA4
- [ ] E7: clinic creates the Google Business Profile with the exact NAP string
- [x] Deployed seo-2026-11-22 live on SG's OK (95c3e60, merged to main) — 2026-11-22
- [x] IndexNow 403 diagnosed: key valid (Yandex 202/200, Seznam 200), only Bing refuses. Hostinger's platform layer 403s any bingbot/Googlebot user agent on this account (ekamvets, wearec4e; no .htaccess rule), the likely reason Bing's key check failed. indexnow.py now also pings Yandex; 30 URLs sent — 2026-11-22
- [ ] SG: add ekamvets.com to Bing Webmaster Tools (import from Search Console after E1) and check Bing's crawl/URL inspection; if Bingbot is blocked, raise it with Hostinger support
- [ ] Mirror E2/E3/E5 into the WordPress staging port (wp/) before cutover

- [ ] Rebuild /if-you-are-an-llm/ page to the two-section spec (en + hi built on branch llm-page, not deployed, awaiting SG copy review) — 2026-11-26
