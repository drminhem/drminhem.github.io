# drminhem.github.io

Existing static GitHub Pages website for drminhem.com. HTML files are served directly; no build or package installation is required.

English pages stay at `/`, `/sodeco.html`, and `/tayouneh.html`. Arabic equivalents live under `/ar/`. Both languages also have `cancer-consultation.html` and `blood-cancer-consultation.html`, plus ten condition guides linked from those hubs. Each file contains its own visible language, title, canonical URL, social metadata, and reciprocal hreflang links. Update both languages when editing content, and keep `sitemap.xml` aligned.

Homepage styling and interactions are shared in `site.css` and `site.js`; clinic and consultation pages use `clinic.css` and `clinic.js`. `language.js` supports legacy `?lang=ar` and homepage `#contact-ar` links. Language choice follows the URL, not stored browser preferences.

## Local preview and verification

```sh
python3 -m http.server 8765 --bind 127.0.0.1
python3 _checks/check_site.py
node _checks/runtime_check.cjs
# Requires an available Playwright installation and Google Chrome:
node _checks/browser_check.cjs
```

If Playwright is installed outside this checkout, set `NODE_PATH` to its parent `node_modules` directory. Set `CHROME_PATH` if Chrome is installed elsewhere. Browser screenshots and results go to `../evidence/`. `_checks/` is excluded from GitHub Pages by Jekyll's underscore-directory convention.

The static check protects every original English/Arabic source line containing American Board wording against baseline `5612dbd`, and verifies metadata, reciprocal language links, internal links/assets/anchors, JSON-LD, map identity, hours removal, and the thirty-page sitemap. Browser checks cover desktop, 390px and 320px widths, JavaScript-disabled navigation, menus, certificate dialogs, legacy URLs, and booking intent. Browser tests do not contact WhatsApp or send analytics.

## Analytics and appointments

`analytics.js` retains the existing GA4 property `G-B46GF8Q2KX`; no new property is introduced. It loads only on the production hostname, and never for `?preview=1`. Pageview URLs exclude query strings and fragments; referrers are reduced to the origin. Contact event attributes remain fixed clinic/language/channel values. Do not add patient details or message text to event parameters or URLs.

The historical `appointment_booking` event still fires before opening WhatsApp. It represents intent to open WhatsApp, **not** a completed appointment, consultation, or confirmed inquiry. `booking.html` stays outside the sitemap and is marked noindex. Use `/booking.html?clinic=sodeco&lang=ar&preview=1` to inspect its Arabic fallback without redirecting.

## Publication boundary

The October 2026 fixes are prepared for review only. Publishing requires explicit authorization before pushing/merging into the GitHub Pages publishing branch. Video consultation availability, fees, duration, payment, and international eligibility are not included. No new hospital affiliation or procedure location is claimed. Multiple myeloma consultations were included after explicit clinical confirmation during review.


## Condition-guide drafts

Ten condition guides are available in English and Arabic: breast, lung, colorectal, prostate, bladder, stomach, lymphoma, leukemia, multiple myeloma, and pancreatic cancer. They were prepared in two batches of five and remain unpublished drafts pending Dr. Minhem’s clinical review. The selection reflects practice priorities, not a claim about national cancer rankings.

The editable bilingual copy and patient-information source URLs are in `_content/batch1.json` and `_content/batch2.json`. The generator reuses the existing consultation styling, portrait, clinic details and booking flow. It also updates hub links, the language-route allowlist, and reciprocal sitemap entries. It does not modify homepage credentials, GA4 initialization, or clinic maps/hours.

```sh
python3 _content/build_guides.py --batch 2
python3 _checks/check_site.py
node _checks/runtime_check.cjs
```

`--batch 1` is for the initial five-page milestone on a checkout that has not generated batch two; the generator does not delete later files. For ordinary edits, regenerate the full set with `--batch 2`.

The draft labels and source-check date are truthful preparation status, not a claim that Dr. Minhem authored or reviewed the text. No schema author or reviewedBy field is assigned. Before publication, record the actual physician review, update the draft-status text and checks accordingly, and obtain explicit publication authorization. Source dates are not a substitute for clinical review.

Every guide has distinct clinical content, three consultation discussion topics, three patient questions, relevant existing reports to bring if available, conditional treatment language, and source links. Mentioning a treatment or investigation does not assert local/on-site provision. The acute-leukemia guide directs suspected or new acute disease to prompt medical assessment, rather than routine booking. No video service, fee, treatment-facility access, or outcome promise is added.

The consultation structure is intended to clarify patient questions and next steps. No improvement in traffic, inquiries, confirmed consultations, or conversion rates has been measured or claimed. Booking links retain only clinic/language parameters; no disease, patient data, or free text is added to analytics events or appointment URLs.
