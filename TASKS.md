# ekam vets site: tasks

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
