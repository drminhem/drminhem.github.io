# drminhem.github.io

Existing static GitHub Pages website for drminhem.com. HTML files are served directly; no build or package installation is required.

English pages stay at `/`, `/sodeco.html`, and `/tayouneh.html`. Arabic equivalents live under `/ar/`. Both languages also have `cancer-consultation.html` and `blood-cancer-consultation.html`, ten condition guides, twelve patient-question guides, and a grouped `patient-guides.html` directory. Each file contains its own visible language, title, canonical URL, social metadata, and reciprocal hreflang links. Update both languages when editing content, and keep `sitemap.xml` aligned.

Homepage styling and interactions are shared in `site.css` and `site.js`; clinic and consultation pages use `clinic.css` and `clinic.js`. The homepage and consultation introductions separate the page purpose from one compact appointment panel. Full addresses and detailed scheduling stay in the clinic sections. `_content/consultation_layout.py` maintains the clinic/consultation appointment panels during full generation; `_content/build_consultation_options.py` fills the explicit video-option position. Condition titles retain Beirut in search metadata while the visible heading avoids repeating the location. Patient-question pages remain answer-first. `language.js` supports legacy `?lang=ar` and homepage `#contact-ar` links. Language choice follows the URL, not stored browser preferences.

## Local preview and verification

```sh
python3 -m http.server 8765 --bind 127.0.0.1
python3 _checks/check_site.py
node _checks/runtime_check.cjs
# Requires an available Playwright installation and Google Chrome:
node _checks/browser_check.cjs
# Focused homepage verification, including accessibility scans:
HOMEPAGE_FOCUS=1 AXE_PATH=/path/to/axe-core/axe.min.js node _checks/browser_check.cjs
```

If Playwright is installed outside this checkout, set `NODE_PATH` to its parent `node_modules` directory. Set `CHROME_PATH` if Chrome is installed elsewhere. Browser screenshots and results go to `../evidence/`. `_checks/` is excluded from GitHub Pages by Jekyll's underscore-directory convention.

The static check protects the original English/Arabic credential lines against baseline `5612dbd`. It allows only the previously authorized clinic-order reversal and the six explicit Internal Medicine wording replacements recorded in `_checks/check_site.py`. It also verifies metadata, reciprocal language links, internal links/assets/anchors, JSON-LD, map identity, hours removal, the 56-page sitemap, four featured homepage guides, four practical FAQs with matching schema, and the full 22-guide directory. Browser checks cover all 56 pages at 320, 390, 768, 1365 and 1440px, standalone control size and clipping, JavaScript-disabled navigation, menus, certificate dialogs, legacy URLs, booking intent, content visibility when the enhancement script fails, prominent portraits at natural proportions with the primary clinic action visible on tested phone screens, and the new guide contents/directory links. A 24-image English/Arabic phone and desktop matrix supports visual review of all shared layouts. Browser tests do not contact WhatsApp or send analytics.

For the new reading templates, run `AXE_PATH=/path/to/axe-core/axe.min.js node _checks/patient_accessibility.cjs` with the same Playwright configuration. This checks all 26 new pages for automated WCAG findings, confirms that the main landmark includes the answer, and tests keyboard skip links. Automated checks do not replace manual accessibility review.

## Analytics and appointments

`analytics.js` retains the existing GA4 property `G-B46GF8Q2KX`; no new property is introduced. It loads only on the production hostname, and never for `?preview=1`. Pageview URLs exclude query strings and fragments; referrers are reduced to the origin. Contact event attributes remain fixed clinic/language/channel values. Do not add patient details or message text to event parameters or URLs.

The historical `appointment_booking` event still fires before opening WhatsApp. It represents intent to open WhatsApp, **not** a completed appointment, consultation, or confirmed inquiry. `booking.html` stays outside the sitemap and is marked noindex. It is crawlable in `robots.txt` so search engines can read that instruction. Use `/booking.html?clinic=sodeco&lang=ar&preview=1` to inspect its Arabic fallback without redirecting. Video requests use the fixed `mode=online` option and a generic bilingual appointment draft, without selecting a physical clinic. Use `/booking.html?mode=online&lang=ar&preview=1` to preview it safely. Availability wording and placement across the existing pages are maintained by `_content/build_consultation_options.py`; the full generator updates them together.

## Publication boundary

Publication of the October 2026 fixes and condition guides was explicitly authorized on 3 October 2026. Subsequent publication actions still require authorization appropriate to the requested changes. On 4 October 2026, Dr. Minhem confirmed that consultations are available remotely for patients outside Beirut; the website uses “video consultation” for clarity. Fees, duration, platform, payment and country-specific eligibility are not advertised. No new hospital affiliation or procedure location is claimed. Multiple myeloma consultations were included after explicit clinical confirmation during review.

On 4 October 2026, the user explicitly approved clarifying the credential as **American Board–Certified in Internal Medicine (USA)** and **حاصل على البورد الأمريكي في الطب الباطني (الولايات المتحدة)**, with the corresponding precise scope in homepage metadata, schema, badges and certification details. This is a narrow exception to the earlier wording freeze, not permission to change other credentials or imply American Board certification in oncology or hematology. Existing Board organization names and official verification links remain protected by the baseline checks.


## Condition guides

Ten condition guides are available in English and Arabic: breast, lung, colorectal, prostate, bladder, stomach, lymphoma, leukemia, multiple myeloma, and pancreatic cancer. They were prepared and checked in two batches of five; publication was subsequently authorized. The selection reflects practice priorities, not a claim about national cancer rankings.

The editable bilingual copy and patient-information source URLs are in `_content/batch1.json` and `_content/batch2.json`. The generator reuses the existing consultation styling, portrait, clinic details and booking flow. It also updates hub links, the language-route allowlist, and reciprocal sitemap entries. It does not modify homepage credentials, GA4 initialization, or clinic maps/hours.

```sh
python3 _content/build_guides.py --batch 2
python3 _checks/check_site.py
node _checks/runtime_check.cjs
```

Regenerate the complete site with `--batch 2`, or omit the argument to use that default. The obsolete `--batch 1` option is rejected before any files are written, so a partial run cannot omit already-published guides from the sitemap, language routes, or directory links.

The displayed source-check date records when the supporting information was checked. It is not a physician-review date. No physician authorship or completed clinical review is claimed, and no schema author or reviewedBy field is assigned. Internal metadata records publication authorization separately from formal clinical review, which has not been recorded. The approved release removes the former draft-only labels without inventing a reviewer attribution.

`_content/page_dates.json` records editorial dates separately for each canonical English and Arabic URL. Change a page's `last_modified` only after a significant content or functionality change to that page; the generator uses it for the sitemap and guide `dateModified` schema. Regenerating files or making a shared styling change does not refresh every date. Each guide also has an independent `sources_checked` date used for its visible source-check label. Update that date only when its supporting information has actually been checked, never merely because wording or layout changed. For a new guide, add both language URLs to this file before generation. Keep these dates accurate and rerun the static check after regeneration.

Every guide has distinct clinical content, three consultation discussion topics, three patient questions, relevant existing reports to bring if available, conditional treatment language, and source links. Mentioning a treatment or investigation does not assert local/on-site provision. The acute-leukemia guide directs suspected or new acute disease to prompt medical assessment, rather than routine booking. The confirmed video option is separate from clinic appointments. No fee, treatment-facility access or outcome promise is added.

The consultation structure is intended to clarify patient questions and next steps. No improvement in traffic, inquiries, confirmed consultations, or conversion rates has been measured or claimed. Booking links retain only clinic/language parameters; no disease, patient data, or free text is added to analytics events or appointment URLs.

On 4 October 2026, Dr. Minhem confirmed consultations for all adult solid cancers, including brain tumors and sarcomas, and the broader hematology/oncology scope. The homepage uses brief cancer examples and one consultation link. The bilingual cancer-consultation hub provides a compact grouped list and distinguishes consultation availability from the smaller set of dedicated guides. This confirmation does not advertise pediatric services or new treatment facilities.

## Patient question guides

Twelve additional topics are prepared in English and Arabic: biopsy spread concerns; chemotherapy benefits and tolerance; immunotherapy suitability; oral cancer treatment; eating during treatment; diet and cancer prevention; possible cancer symptoms; screening; benign blood conditions; easy bruising; targeted therapy; and genetic testing in cancer. The grouped directory retains all 22 guides: these twelve topics and the ten cancer-type guides. The homepage features four patient questions about biopsy, chemotherapy, treatment advances and immunotherapy, with a doorway to the complete directory. Its four FAQs address appointment logistics; treatment explanations live in the linked guides. Benign blood conditions have a full fourth consultation card alongside new cancer diagnoses, second opinions and blood cancers, with a direct link to the existing guide.

The benign hematology labels use “Benign hematology consultations” and “استشارات أمراض الدم الحميدة”; existing URLs retain `non-cancer-blood-conditions.html`. The guide explains that benign means non-cancerous, not necessarily mild. The homepage identity uses “Hematology & Oncology · U.S.-trained,” with its existing Arabic equivalent. Tayouneh addresses start with Dubai Building beneath the clinic heading. Cancer types use a uniform list of names in both languages.

The treatment-advances question links to `patient-guides.html#treatment-advances`, a brief sourced overview before the existing treatment guides. It describes meaningful progress for selected patient groups, biomarker-informed treatment selection and chemotherapy's continuing role. The overview does not advertise a universal improvement percentage, local availability of particular drugs or tests, or a guaranteed response. Its four NCI sources were checked on 4 October 2026; this is not a physician-review attribution.

Editable text is in `_content/patient_treatment_one.json`, `patient_treatment_two.json`, `patient_nutrition.json`, `patient_assessment.json`, and `patient_hematology.json`, and `patient_precision.json`. `_content/build_patient_guides.py` is called by the full `build_guides.py --batch 2` command, which updates all pages, language routes and the sitemap together. `_content/patient_generated.json` records this expansion separately from the previously published condition guides. Publication of this new set was explicitly authorized on 4 October 2026 (Beirut date); no formal physician-review attribution is recorded.

Screening and cancer-risk assessment consultations for people without symptoms were explicitly confirmed by Dr. Minhem on 4 October 2026 (Beirut date). No screening tests or treatment administration are advertised as taking place at either clinic. New source-check dates reflect the sources checked during preparation, not a completed physician review. Content emphasizes the patient's decision and what a consultation can clarify. Treatment and nutrition safety notes follow the main decision guidance; symptom/bleeding urgency remains prominent. Treatment nutrition and prevention nutrition are deliberately separate, with no restrictive diet, supplement, cure or prevention guarantees.
