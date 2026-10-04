"""Patient question guides. Called by build_guides.py so all routes stay in sync."""
from pathlib import Path
from html import escape
from datetime import date
import json, re

ROOT = Path(__file__).resolve().parents[1]
FILES = ['patient_treatment_one.json', 'patient_treatment_two.json', 'patient_precision.json', 'patient_nutrition.json', 'patient_assessment.json', 'patient_hematology.json']
GROUPS = {
 'treatment': {'en': 'Understanding cancer treatment', 'ar': 'فهم علاج السرطان'},
 'nutrition': {'en': 'Food and nutrition', 'ar': 'الغذاء والتغذية'},
 'assessment': {'en': 'Symptoms and screening', 'ar': 'الأعراض والكشف المبكر'},
 'hematology': {'en': 'Benign blood conditions', 'ar': 'أمراض الدم الحميدة'},
}
JUMP_LABELS = {
 'en': {'treatment':'Treatment options', 'nutrition':'Nutrition', 'assessment':'Symptoms & screening', 'hematology':'Blood conditions', 'cancer-types':'Cancer types'},
 'ar': {'treatment':'خيارات العلاج', 'nutrition':'التغذية', 'assessment':'الأعراض والكشف المبكر', 'hematology':'أمراض الدم', 'cancer-types':'أنواع السرطان'},
}
COPY = {
 'en': {
  'brand':'Dr. Mohamad Minhem', 'directory':'Patient guides', 'language':'العربية',
  'skip':'Skip to content', 'navigation':'Main navigation', 'on_page':'In this guide',
  'questions':'Questions to ask at your consultation', 'related':'Related guides',
  'sources':'Patient information sources', 'checked':'Sources checked',
  'source_note':'General patient information; your medical team can explain how it applies to you.',
  'care':'Discuss your questions', 'care_text':'Bring your existing reports, medication list, and questions to a consultation with Dr. Mohamad Minhem.',
  'book':'Request a consultation at Sodeco Clinic', 'call':'Call',
  'location':'Sodeco Square, Block B, 6th Floor, Beirut', 'other':'Tayouneh clinic and appointments',
  'when':'Both clinics see patients by appointment, with flexible scheduling. Confirm a suitable time before visiting.',
  'disclaimer':'This guide provides general information, not an individual diagnosis or treatment plan. For urgent symptoms, seek medical care rather than waiting for an appointment request.',
  'index_title':'Cancer and blood-health guides',
  'index_description':'Clear guides to cancer treatment, nutrition, symptoms, screening, and blood conditions, in English and Arabic.',
  'index_answer':'Clear answers about treatment, nutrition, screening and blood conditions. Choose the question that matters to you.',
  'types':'Guides by cancer type', 'consultations':'Cancer consultations and second opinions',
  'home':'Home and clinics', 'browse':'Browse all patient guides', 'browse_types':'Browse by cancer type',
  'advances_title':'How have cancer treatments improved?',
  'advances_text':'Targeted therapies and immunotherapy have improved outcomes for selected groups of patients; some responses last for years. Molecular and other tumor tests can help identify suitable options. Treatment still depends on the cancer type, stage and your health. Chemotherapy remains important and may be used alone or combined with other treatments.',
  'advances_sources':'Sources',
 },
 'ar': {
  'brand':'د. محمد منعم', 'directory':'معلومات للمرضى', 'language':'English',
  'skip':'انتقل إلى المحتوى', 'navigation':'التنقل الرئيسي', 'on_page':'في هذه الصفحة',
  'questions':'أسئلة يمكنك طرحها خلال الاستشارة', 'related':'مواضيع ذات صلة',
  'sources':'مصادر للمزيد من المعلومات', 'checked':'تاريخ التحقّق من المصادر',
  'source_note':'معلومات عامة للمرضى؛ يمكن لفريقك الطبي توضيح ما يناسب حالتك منها.',
  'care':'ناقش أسئلتك مع الطبيب', 'care_text':'يمكنك مناقشة أسئلتك مع د. محمد منعم. أحضر إلى الاستشارة تقاريرك المتوفّرة وقائمة أدويتك.',
  'book':'اطلب استشارة في عيادة سوديكو', 'call':'اتصل',
  'location':'سوديكو سكوير، المبنى B، الطابق السادس، بيروت', 'other':'عيادة الطيونة والمواعيد',
  'when':'المواعيد في العيادتين تُرتَّب مسبقاً وبمرونة. تواصل معنا لاختيار وقت مناسب وتأكيده قبل الحضور.',
  'disclaimer':'تقدّم هذه الصفحة معلومات عامة، ولا تغني عن تشخيص طبي أو خطة علاج تناسب حالتك. إذا ظهرت أعراض تستدعي تقييماً عاجلاً، اطلب الرعاية الطبية ولا تنتظر الردّ على طلب موعد.',
  'index_title':'إجابات عن أسئلتك', 'index_meta_title':'السرطان وأمراض الدم: معلومات للمرضى',
  'index_description':'معلومات للمرضى حول علاج السرطان والتغذية والأعراض والكشف المبكر وأمراض الدم، بلغة واضحة تساعدك على فهم خياراتك.',
  'index_answer':'إجابات واضحة عن العلاج والتغذية والكشف المبكر وأمراض الدم. اختر السؤال الذي يهمّك.',
  'types':'معلومات بحسب نوع السرطان', 'consultations':'استشارات السرطان والرأي الطبي الثاني',
  'home':'الرئيسية والعيادات', 'browse':'تصفّح جميع المواضيع', 'browse_types':'تصفّح بحسب نوع السرطان',
  'advances_title':'كيف تطوّرت علاجات السرطان؟',
  'advances_text':'حسّنت العلاجات الموجّهة والمناعية نتائج العلاج لدى فئات معيّنة من المرضى، وقد تستمر الاستجابة سنوات لدى بعضهم. تساعد الفحوص الجزيئية وغيرها من فحوص الورم في تحديد الخيارات المناسبة. يعتمد العلاج على نوع السرطان ومرحلته وصحتك العامة، ويظلّ العلاج الكيميائي مهمّاً، سواء وحده أو مع علاجات أخرى.',
  'advances_sources':'المصادر',
 }
}

def e(value):
 return escape(value, quote=True)

def head_for(slug, lang, title, description, schema):
 base = '/ar/' if lang == 'ar' else '/'
 head = (ROOT / (base.lstrip('/') + 'cancer-consultation.html')).read_text().split('</head>')[0] + '</head>'
 head = head.replace('cancer-consultation.html', slug + '.html')
 full_title = title + (' — Dr. Mohamad Minhem' if lang == 'en' else ' — د. محمد منعم')
 head = re.sub(r'<title>.*?</title>', '<title>' + e(full_title) + '</title>', head)
 for key, value in [('description', description), ('og:description', description), ('og:title', full_title), ('og:url', 'https://drminhem.com' + base + slug + '.html')]:
  head = re.sub(r'(<meta (?:name|property)="' + key + r'" content=")[^"]*', lambda m: m[1] + e(value), head)
 head = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>', head, flags=re.S)
 return head

def navigation(slug, lang):
 c = COPY[lang]; base = '/ar/' if lang == 'ar' else '/'; other = '/' if lang == 'ar' else '/ar/'; alternate = 'en' if lang == 'ar' else 'ar'
 return f'''<a class="skipLink" href="#main">{c['skip']}</a>
<nav class="siteNav" aria-label="{c['navigation']}"><div class="wrap navInner">
<a class="brand" href="{base}">{c['brand']}</a><div class="navActions">
<a class="navLink" href="{base}patient-guides.html">{c['directory']}</a>
<a class="langButton" data-language-link href="{other}{slug}.html" hreflang="{alternate}" lang="{alternate}">{c['language']}</a>
</div></div></nav>'''

def footer(lang):
 c = COPY[lang]; base = '/ar/' if lang == 'ar' else '/'
 return f'''<footer class="footer"><div class="wrap footerInner"><span>© <span data-year>2026</span> {c['brand']}</span><a href="{base}">{c['home']}</a></div></footer>
<script src="/clinic.js"></script></body></html>'''

def consultation(lang, item=None):
 c = COPY[lang]; base = '/ar/' if lang == 'ar' else '/'
 note = item[lang].get('consultation_note', c['care_text']) if item else c['care_text']
 return f'''<section class="card patientConsultation" aria-labelledby="consultation"><h2 id="consultation">{c['care']}</h2><p>{e(note)}</p>
<div class="actions"><a class="button whatsapp" href="/booking.html?clinic=sodeco&amp;lang={lang}" target="_blank" rel="noopener">{c['book']}</a><a class="button secondary" href="tel:+96181902903" data-track="contact_phone">{c['call']} <span class="phoneLtr">+961 81 902 903</span></a></div>
<p class="clinicLocation"><a href="{base}sodeco.html">{c['location']}</a></p><p><a href="{base}tayouneh.html">{c['other']}</a></p><p>{c['when']}</p></section>'''

def guide_page(item, lang, items, dates):
 c = COPY[lang]; d = item[lang]; base = '/ar/' if lang == 'ar' else '/'; slug = item['slug']; path = base + slug + '.html'
 schema = {'@context':'https://schema.org', '@type':'MedicalWebPage', 'name':d['title'], 'description':d['description'], 'url':'https://drminhem.com' + path, 'inLanguage':lang,
  'dateModified':dates[path]['last_modified'], 'isPartOf':{'@type':'WebSite','url':'https://drminhem.com/'}, 'citation':[s['url'] for s in item['sources']]}
 sections = []
 for section in d['sections']:
  body = ''.join('<p>' + e(p) + '</p>' for p in section.get('paragraphs', []))
  if section.get('bullets'): body += '<ul class="details">' + ''.join('<li>' + e(p) + '</li>' for p in section['bullets']) + '</ul>'
  sections.append(f'<section class="patientSection" aria-labelledby="topic-{e(section["id"])}"><h2 id="topic-{e(section["id"])}">{e(section["title"])}</h2>{body}</section>')
 toc = ''.join(f'<li><a href="#topic-{e(s["id"])}">{e(s["title"])}</a></li>' for s in d['sections'])
 urgency = ''
 if d.get('urgent'):
  urgency = f'<aside class="patientUrgent" aria-labelledby="urgent"><h2 id="urgent">{e(d["urgent"]["title"])}</h2><p>{e(d["urgent"]["text"])}</p></aside>'
 urgent_first = item['category'] in {'assessment', 'hematology'}
 questions = ''.join('<li>' + e(q) + '</li>' for q in d['questions'])
 by_slug = {i['slug']:i for i in items}
 related = ''.join(f'<li><a href="{base}{e(s)}.html">{e(by_slug[s][lang]["title"])}</a></li>' for s in d['related'])
 sources = ''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener" lang="en">{e(s["title"])}</a></li>' for s in item['sources'])
 checked = dates[path]['sources_checked']
 checked_date = date.fromisoformat(checked)
 months = ['January','February','March','April','May','June','July','August','September','October','November','December']
 # Arabic and English labels use the same explicitly recorded source date.
 if lang == 'ar': months = ['كانون الثاني','شباط','آذار','نيسان','أيار','حزيران','تموز','آب','أيلول','تشرين الأول','تشرين الثاني','كانون الأول']
 checked_label = f'{checked_date.day} {months[checked_date.month - 1]} {checked_date.year}'
 return head_for(slug, lang, d['title'], d['description'], schema) + f'''
<!-- Generated from _content/patient_*.json. -->
<body data-lang="{lang}" class="consultation patientGuide">{navigation(slug, lang)}
<main id="main" tabindex="-1"><header class="hero"><div class="wrap readingWidth"><a class="patientBack" href="{base}patient-guides.html">{c['directory']}</a>
<p class="eyebrow">{GROUPS[item['category']][lang]}</p><h1>{e(d['title'])}</h1><p class="lead">{e(d['answer'])}</p>
<a class="patientDiscuss" href="#consultation">{c['care']}</a></div></header>
<div class="content"><div class="wrap readingWidth">{urgency if urgent_first else ""}
<nav class="patientContents" aria-labelledby="contents"><h2 id="contents">{c['on_page']}</h2><ul>{toc}</ul></nav>
{''.join(sections)}
{urgency if not urgent_first else ''}
<section class="patientSection" aria-labelledby="questions"><h2 id="questions">{c['questions']}</h2><ul class="details">{questions}</ul></section>
{consultation(lang, item)}
<section class="patientSection" aria-labelledby="related"><h2 id="related">{c['related']}</h2><ul class="patientRelated">{related}</ul><a href="{base}patient-guides.html">{c['browse']}</a></section>
<section class="guideSources" aria-labelledby="sources"><h2 class="sectionTitle" id="sources">{c['sources']}</h2><ul class="details">{sources}</ul><p>{c['source_note']}</p><p class="reviewStatus" data-source-check="{checked}">{c['checked']}: {checked_label}.</p></section>
<p class="guideDisclaimer">{c['disclaimer']}</p></div></div></main>{footer(lang)}
'''

def directory_page(items, conditions, lang, dates):
 c = COPY[lang]; base = '/ar/' if lang == 'ar' else '/'; path = base + 'patient-guides.html'
 schema = {'@context':'https://schema.org', '@type':'CollectionPage','name':c.get('index_meta_title', c['index_title']),'description':c['index_description'],'url':'https://drminhem.com' + path,'inLanguage':lang,'dateModified':dates[path]['last_modified']}
 groups = []
 for category, labels in GROUPS.items():
  links = ''.join(f'<a class="guideLink" href="{base}{i["slug"]}.html">{e(i[lang]["title"])}</a>' for i in items if i['category'] == category)
  heading = f'<h2 class="sectionTitle" id="{category}">{labels[lang]}</h2>'
  if category == 'treatment':
   sources = [
    ('https://www.cancer.gov/types/skin/research', 'NCI: Progress in melanoma treatment' if lang == 'en' else 'المعهد الوطني للسرطان: تطوّر علاج الميلانوما'),
    ('https://www.cancer.gov/research/progress/discovery/gleevec', 'NCI: How targeted therapy changed CML treatment' if lang == 'en' else 'المعهد الوطني للسرطان: أثر العلاج الموجّه في اللوكيميا النخاعية المزمنة'),
    ('https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment', 'NCI: Biomarker testing for treatment selection' if lang == 'en' else 'المعهد الوطني للسرطان: فحوص المؤشرات الحيوية لاختيار العلاج'),
    ('https://www.cancer.gov/about-cancer/treatment/types/targeted-therapies', 'NCI: Targeted therapy' if lang == 'en' else 'المعهد الوطني للسرطان: العلاج الموجّه'),
   ]
   source_links = ''.join(f'<li><a href="{url}" target="_blank" rel="noopener">{e(label)}</a></li>' for url,label in sources)
   heading = f'<div class="treatmentAdvances" id="treatment-advances"><h2 class="sectionTitle" id="treatment">{c["advances_title"]}</h2><p>{c["advances_text"]}</p><details class="advancesSources"><summary>{c["advances_sources"]}</summary><ul>{source_links}</ul></details></div>'
  groups.append(f'<section class="patientGroup" aria-labelledby="{category}">{heading}<div class="guideLinks">{links}</div></section>')
 links = ''.join(f'<a class="guideLink" href="{base}{i["slug"]}.html">{e(i[lang]["name"])}</a>' for i in conditions)
 return head_for('patient-guides', lang, c.get('index_meta_title', c['index_title']), c['index_description'], schema) + f'''
<body data-lang="{lang}" class="consultation patientDirectory">{navigation('patient-guides', lang)}
<main id="main" tabindex="-1"><header class="hero"><div class="wrap"><p class="eyebrow">{c['directory']}</p><h1>{c['index_title']}</h1><p class="lead">{c['index_answer']}</p>
<nav class="directoryJump" aria-label="{c['directory']}">{''.join(f'<a href="#{key}">{e(label)}</a>' for key,label in JUMP_LABELS[lang].items())}</nav></div></header>
<div class="content"><div class="wrap">{''.join(groups)}
<section class="patientGroup" aria-labelledby="cancer-types"><h2 class="sectionTitle" id="cancer-types">{c['types']}</h2><div class="guideLinks">{links}</div><a href="{base}cancer-consultation.html">{c['consultations']}</a></section>
{consultation(lang)}</div></div></main>{footer(lang)}
'''

def build(conditions, dates):
 items = []
 for name in FILES: items.extend(json.loads((ROOT / '_content' / name).read_text()))
 assert len({i['slug'] for i in items}) == len(items)
 for lang in ['en', 'ar']:
  base = 'ar/' if lang == 'ar' else ''; prefix = '/' + base
  for item in items: (ROOT / (base + item['slug'] + '.html')).write_text(guide_page(item, lang, items, dates))
  (ROOT / (base + 'patient-guides.html')).write_text(directory_page(items, conditions, lang, dates))
  c = COPY[lang]
  # Keep the homepage's selected questions and the doorways to the full guide directory.
  home = ROOT / (base + 'index.html'); text = home.read_text()
  link = f'<p class="patientDirectoryLink"><a class="btn primary" href="{prefix}patient-guides.html">{c["browse"]}</a><a class="guideBrowseTypes" href="{prefix}patient-guides.html#cancer-types">{c["browse_types"]}</a></p>'
  if 'class="patientDirectoryLink"' in text: text = re.sub(r'<p class="patientDirectoryLink">.*?</p>', link, text)
  else:
   text = re.sub(r'(<section id="guides-' + lang + r'".*?)(\n        </div>\n      </section>)', lambda m: m[1] + '\n          ' + link + m[2], text, count=1, flags=re.S)
  phrase = 'Other blood conditions:' if lang == 'en' else 'أمراض الدم الأخرى:'
  text = text.replace(f'<b>{phrase}</b>', f'<b><a href="{prefix}non-cancer-blood-conditions.html">{phrase}</a></b>')
  home.write_text(text)
  # A short relevant doorway from both consultation hubs; no new wall of homepage links.
  for name in ['cancer-consultation', 'blood-cancer-consultation']:
   page = ROOT / (base + name + '.html'); text = page.read_text()
   heading = 'Questions about treatment?' if lang == 'en' else 'لديك أسئلة عن العلاج؟'
   note = 'Biopsy, chemotherapy, immunotherapy, cancer tablets, nutrition, and more.' if lang == 'en' else 'إجابات عن أسئلتك حول الخزعة والعلاج الكيميائي والمناعي والأدوية التي تؤخذ عن طريق الفم والتغذية وغيرها.'
   block = f'<!-- PATIENT_GUIDES_START --><section class="patientGuideDoor"><h2 class="sectionTitle">{heading}</h2><p>{note}</p><a class="button secondary" href="{prefix}patient-guides.html">{c["browse"]}</a></section><!-- PATIENT_GUIDES_END -->'
   if '<!-- PATIENT_GUIDES_START -->' in text: text = re.sub(r'<!-- PATIENT_GUIDES_START -->.*?<!-- PATIENT_GUIDES_END -->', block, text, flags=re.S)
   else: text = text.replace('    <section aria-labelledby="locations">', block + '\n    <section aria-labelledby="locations">', 1)
   page.write_text(text)
 (ROOT / '_content/patient_generated.json').write_text(json.dumps({'slugs':[i['slug'] for i in items], 'directory':'patient-guides', 'clinical_review':'not_recorded', 'publication':'authorized', 'screening_consultations':'confirmed_by_physician_2026-10-04'}, indent=2) + '\n')
 return [i['slug'] for i in items] + ['patient-guides']
