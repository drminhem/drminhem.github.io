"""Generate static bilingual condition guides. Clinical drafts require physician review.
Run: python3 _content/build_guides.py --batch 1  (or --batch 2 for all ten).
"""
from pathlib import Path
from html import escape
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-03'
ORDER=['breast-cancer','lung-cancer','colorectal-cancer','prostate-cancer','bladder-cancer',
       'stomach-cancer','lymphoma','leukemia','multiple-myeloma','pancreatic-cancer']
BLOOD={'lymphoma','leukemia','multiple-myeloma'}
LABELS={
 'en':{
  'brand':'Dr. Mohamad Minhem','home':'Home & clinics','language':'العربية',
  'skip':'Skip to content','navigation':'Main navigation','eyebrow':'Cancer consultations · Beirut',
  'draft':'Draft for clinical review','review':'Clinical review by Dr. Mohamad Minhem is pending. This draft has not been published.',
  'date':'Sources checked and draft updated: 3 October 2026.',
  'help':'How I can help','tailored':'A treatment plan tailored to your cancer, test results, overall health and preferences, informed by current evidence.',
  'bring':'Reports to bring, if available','existing':'Bring the reports you already have. This list does not mean every test is needed.',
  'medications':'Please also bring your medication list, previous treatment records, and questions.',
  'book':'Request a consultation','call':'Call',
  'when':'By appointment only, with flexible scheduling at Sodeco and Tayouneh. Please confirm a suitable time before visiting.',
  'clinics':'Choose your clinic','sodeco':'Sodeco Clinic','sodeco_address':'Sodeco Square, Block B, 6th Floor, Beirut',
  'tayouneh':'Tayouneh Clinic','tayouneh_address':'Tayouneh Clinics, Dubai Building, First Floor, Old Saida Road, Beirut',
  'details':'Address & appointment details','sources':'Patient information sources',
  'source_note':'These sources explain general options. The consultation focuses on what is appropriate for your diagnosis and health.',
  'related':'More consultation information','cancer':'New cancer diagnosis & second opinions','blood':'Blood-cancer consultations',
  'guides':'Consultation guides by cancer type','blood_guides':'Explore blood-cancer consultation guides',
  'guides_note':'Read about the questions, test results, and decisions that may matter for your consultation.',
  'emergency':'This information supports a consultation and does not provide an individual treatment plan. This clinic is not an emergency service; for an emergency, go to the nearest emergency department.'},
 'ar':{
  'brand':'د. محمد منعم','home':'الرئيسية والعيادات','language':'English',
  'skip':'انتقل إلى المحتوى','navigation':'التنقل الرئيسي','eyebrow':'استشارات الأورام · بيروت',
  'draft':'مسودة للمراجعة الطبية','review':'بانتظار المراجعة الطبية من الدكتور محمد منعم. لم تُنشر هذه المسودة بعد.',
  'date':'تاريخ التحقّق من المصادر وتحديث المسودة: 3 تشرين الأول 2026.',
  'help':'كيف أساعدك؟','tailored':'خطة علاج تراعي نوع السرطان ونتائج فحوصاتك وصحتك العامة وتفضيلاتك، وتستند إلى الأدلة العلمية الحالية.',
  'bring':'تقارير تحضرها إن توفّرت','existing':'أحضر التقارير المتوفّرة لديك. لا تعني هذه القائمة أنّك تحتاج إلى كل فحص مذكور.',
  'medications':'أحضر أيضاً قائمة أدويتك وسجلات العلاجات السابقة والأسئلة التي تودّ مناقشتها.',
  'book':'اطلب استشارة','call':'اتصل',
  'when':'بموعد مسبق فقط، مع مرونة في المواعيد في سوديكو والطيونة. يُرجى تأكيد وقت مناسب قبل الحضور.',
  'clinics':'اختر العيادة المناسبة لك','sodeco':'عيادة سوديكو','sodeco_address':'سوديكو سكوير، المبنى B، الطابق السادس، بيروت',
  'tayouneh':'عيادة الطيونة','tayouneh_address':'عيادات الطيونة، مبنى دبي، الطابق الأول، طريق صيدا القديمة، بيروت',
  'details':'العنوان وتفاصيل المواعيد','sources':'مصادر معلومات للمرضى',
  'source_note':'تشرح هذه المصادر خيارات عامة. وتركّز الاستشارة على ما يناسب تشخيصك وصحتك.',
  'related':'معلومات إضافية عن الاستشارات','cancer':'تشخيص جديد للسرطان ورأي طبي ثانٍ','blood':'استشارات سرطانات الدم',
  'guides':'أدلة الاستشارة بحسب نوع السرطان','blood_guides':'أدلة استشارات سرطانات الدم',
  'guides_note':'تعرّف إلى الأسئلة ونتائج الفحوصات والقرارات التي قد تهمّك في الاستشارة.',
  'emergency':'تساعدك هذه المعلومات على التحضير للاستشارة، ولا تمثّل خطة علاج لحالتك. هذه العيادة ليست لخدمات الطوارئ؛ في الحالات الطارئة توجّه إلى أقرب قسم طوارئ.'}
}
def e(s):return escape(s,quote=True)
def paragraph(s):return '<p>'+e(s)+'</p>'
def list_items(items):return ''.join('<li>'+e(s)+'</li>' for s in items)
def page_for(item,lang):
 c=LABELS[lang];d=item[lang];base='/ar/' if lang=='ar' else '/';other='/' if lang=='ar' else '/ar/'
 alternate='en' if lang=='ar' else 'ar';slug=item['slug'];path=base+slug+'.html';url='https://drminhem.com'+path
 title=(d['title']+' in Beirut — Dr. Mohamad Minhem') if lang=='en' else (d['title']+' في بيروت — د. محمد منعم')
 # The pre-existing hub supplies the established site fonts, portrait and analytics.
 hub=(ROOT/(base.lstrip('/')+'cancer-consultation.html')).read_text()
 head=hub.split('</head>')[0]+'</head>'
 head=head.replace('cancer-consultation.html',slug+'.html')
 head=re.sub(r'<title>.*?</title>','<title>'+e(title)+'</title>',head)
 for key,val in [('description',d['lead']),('og:description',d['lead']),('og:title',title),('og:url',url)]:
  head=re.sub(r'(<meta (?:name|property)="'+key+r'" content=")[^"]*',lambda m:m[1]+e(val),head)
 schema={'@context':'https://schema.org','@type':'MedicalWebPage','name':title,'description':d['lead'],
         'url':url,'inLanguage':lang,'dateModified':DATE,'about':{'@type':'MedicalCondition','name':d['name']},
         'isPartOf':{'@type':'WebSite','url':'https://drminhem.com/'},'citation':[s['url'] for s in item['sources']]}
 head=re.sub(r'<script type="application/ld\+json">.*?</script>',
             '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>',head,flags=re.S)
 topics='\n'.join('<article class="quickCard"><h3>'+e(t['title'])+'</h3>'+paragraph(t['text'])+'</article>' for t in d['topics'])
 sources='\n'.join('<li><a href="'+e(s['url'])+'" target="_blank" rel="noopener" lang="en">'+e(s['title'])+'</a></li>' for s in item['sources'])
 clinics='\n'.join(f'''<section class="card"><h3>{c[x]}</h3>
<address class="address">{c[x+'_address']}</address>
<div class="actions"><a class="button secondary" href="{base}{x}.html">{c['details']}</a>
<a class="button whatsapp" href="/booking.html?clinic={x}&amp;lang={lang}" target="_blank" rel="noopener">{c['book']}</a></div></section>''' for x in ['sodeco','tayouneh'])
 parent='blood-cancer-consultation' if slug in BLOOD else 'cancer-consultation'
 parent_label=c['blood'] if slug in BLOOD else c['cancer']
 return head+f'''
<!-- Generated from _content/batch*.json by _content/build_guides.py. Clinical review pending. -->
<body data-lang="{lang}" class="consultation conditionGuide">
  <a class="skipLink" href="#main">{c['skip']}</a>
  <nav class="siteNav" aria-label="{c['navigation']}"><div class="wrap navInner">
    <a class="brand" href="{base}">{c['brand']}</a>
    <div class="navActions"><a class="navLink" href="{base}cancer-consultation.html">{c['cancer']}</a>
      <a class="langButton" data-language-link href="{other}{slug}.html" hreflang="{alternate}" lang="{alternate}">{c['language']}</a>
    </div>
  </div></nav>
  <header class="hero"><div class="wrap heroGrid"><div>
    <a class="backLink" href="{base}{parent}.html">{parent_label}</a>
    <p class="draftLabel">{c['draft']}</p>
    <div class="eyebrow">{c['eyebrow']}</div>
    <h1>{e(d['title'])}{' in Beirut' if lang=='en' else ' في بيروت'}</h1><p class="lead">{e(d['lead'])}</p>
    <div class="actions"><a class="button whatsapp" href="/booking.html?clinic=general&amp;lang={lang}" target="_blank" rel="noopener">{c['book']}</a>
      <a class="button secondary" href="tel:+96181902903" data-track="contact_phone">{c['call']} <span class="phoneLtr">+961 81 902 903</span></a></div>
    <p class="notice">{c['when']}</p>
  </div><div class="portrait"><picture>
    <source type="image/webp" srcset="/portrait-480.webp 480w, /portrait-900.webp 900w" sizes="(max-width: 520px) 196px, (max-width: 800px) 240px, 290px">
    <img src="/portrait.jpg" alt="{c['brand']}" width="1195" height="1316" decoding="async" fetchpriority="high">
  </picture></div></div></header>
  <main class="content" id="main"><div class="wrap">
    <section class="card"><h2>{e(d['intro_title'])}</h2>{paragraph(d['intro'])}</section>
    <section aria-labelledby="help"><h2 class="sectionTitle" id="help">{c['help']}</h2>
      <p class="guideIntro">{c['tailored']}</p><div class="quickGrid">{topics}</div>
    </section>
    <section class="card guideSection"><h2>{c['bring']}</h2><p>{c['existing']}</p>
      <ul class="details">{list_items(d['reports'])}</ul><p>{c['medications']}</p>
    </section>
    <section class="card guideSection"><h2>{e(d['question_title'])}</h2><ul class="details">{list_items(d['questions'])}</ul></section>
    <section aria-labelledby="locations"><h2 class="sectionTitle" id="locations">{c['clinics']}</h2><div class="grid">{clinics}</div></section>
    <section class="guideSources" aria-labelledby="sources"><h2 class="sectionTitle" id="sources">{c['sources']}</h2>
      <ul class="details">{sources}</ul><p>{c['source_note']}</p>
      <p class="reviewStatus" data-clinical-review="pending">{c['date']} {c['review']}</p>
    </section>
    <p class="guideDisclaimer">{c['emergency']}</p>
    <section><h2 class="sectionTitle">{c['related']}</h2><div class="actions">
      <a class="button secondary" href="{base}cancer-consultation.html">{c['cancer']}</a>
      <a class="button secondary" href="{base}blood-cancer-consultation.html">{c['blood']}</a>
    </div></section>
  </div></main>
  <footer class="footer"><div class="wrap footerInner"><span>© <span data-year>2026</span> {c['brand']}</span><a href="{base}">drminhem.com</a></div></footer>
  <script src="/clinic.js"></script>
</body>
</html>
'''
def update_hub(items,lang,blood=False):
 base='/ar/' if lang=='ar' else '/';c=LABELS[lang];name='blood-cancer-consultation' if blood else 'cancer-consultation'
 p=ROOT/(base.lstrip('/')+name+'.html');s=p.read_text()
 chosen=[i for i in items if not blood or i['slug'] in BLOOD]
 if not chosen:return
 links='\n'.join(f'<a class="guideLink" href="{base}{i["slug"]}.html">{e(i[lang]["name"])}</a>' for i in chosen)
 section=f'''<!-- CONDITION_GUIDES_START -->
    <section class="guideDirectory" aria-labelledby="condition-guides"><h2 class="sectionTitle" id="condition-guides">{c['blood_guides'] if blood else c['guides']}</h2>
      <p>{c['guides_note']}</p><div class="guideLinks">{links}</div>
    </section>
    <!-- CONDITION_GUIDES_END -->'''
 if '<!-- CONDITION_GUIDES_START -->' in s:s=re.sub(r'<!-- CONDITION_GUIDES_START -->.*?<!-- CONDITION_GUIDES_END -->',section,s,flags=re.S)
 else:s=s.replace('    <section aria-labelledby="locations">',section+'\n    <section aria-labelledby="locations">',1)
 p.write_text(s)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,choices=[1,2],default=2);args=parser.parse_args()
 items=[]
 for batch in range(1,args.batch+1):items+=json.loads((ROOT/f'_content/batch{batch}.json').read_text())
 assert len(items)==5*args.batch
 assert {i['slug'] for i in items}==set(ORDER[:5*args.batch])
 items.sort(key=lambda i:ORDER.index(i['slug']))
 for item in items:
  assert len(item['sources'])>=2,item['slug']
  for lang in ['en','ar']:
   assert len(item[lang]['topics'])==3
   assert len(item[lang]['questions'])==3
   (ROOT/(('ar/' if lang=='ar' else '')+item['slug']+'.html')).write_text(page_for(item,lang))
 for lang in ['en','ar']:
  update_hub(items,lang);update_hub(items,lang,True)
 names=['','sodeco.html','tayouneh.html','cancer-consultation.html','blood-cancer-consultation.html']+[i['slug']+'.html' for i in items]
 entries=[]
 for name in names:
  en='https://drminhem.com/'+name;ar='https://drminhem.com/ar/'+name
  for url in [en,ar]:
   entries.append(f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{DATE}</lastmod>\n    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>\n    <xhtml:link rel="alternate" hreflang="ar" href="{ar}"/>\n    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>\n  </url>')
 (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(entries)+'\n</urlset>\n')
 (ROOT/'_content/generated.json').write_text(json.dumps({'date':DATE,'batch':args.batch,'slugs':[i['slug'] for i in items],'clinical_review':'pending'},indent=2)+'\n')
 language=ROOT/'language.js';s=language.read_text();s=re.sub(r'  const pages = \[.*?\];', '  const pages = '+json.dumps(['/'+n for n in names])+';',s);language.write_text(s)
 print(f'Generated {len(items)*2} bilingual condition pages; {len(names)*2} sitemap URLs; clinical review pending.')
if __name__=='__main__':main()
