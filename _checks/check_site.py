"""Regression checks for static pages. Run from the repository: python3 _checks/check_site.py."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin, unquote, parse_qs
from urllib.robotparser import RobotFileParser
from datetime import date
import json, re, subprocess, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self, text):
  super().__init__(); self.tags=[];self.ids=set();self.titles=[];self.in_title=False;self.feed(text)
 def handle_starttag(self, tag, attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if 'id' in a:
   assert a['id'] not in self.ids, 'Duplicate ID: '+a['id']
   self.ids.add(a['id'])
  if tag=='title':self.in_title=True
 def handle_startendtag(self, tag, attrs):self.handle_starttag(tag,attrs)
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.in_title:self.titles.append(data)
 def find(self,tag,**attrs):return [a for t,a in self.tags if t==tag and all(a.get(k)==v for k,v in attrs.items())]
files={p.relative_to(ROOT).as_posix():p.read_text() for p in ROOT.glob('*.html')}
files.update({p.relative_to(ROOT).as_posix():p.read_text() for p in ROOT.glob('ar/*.html')})
pages={k:Page(v) for k,v in files.items()}
site='https://drminhem.com'
urls=[]
for filename,text in files.items():
 p=pages[filename];lang='ar' if filename.startswith('ar/') else 'en'
 assert p.find('html',lang=lang),filename
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(raw)
 if filename=='booking.html':
  assert p.find('meta',name='robots',content='noindex,nofollow');continue
 path='/'+filename.replace('index.html','');url=site+path;urls.append(url)
 canonical=p.find('link',rel='canonical');assert len(canonical)==1 and canonical[0]['href']==url,(filename,canonical)
 alternates={a['hreflang']:a['href'] for a in p.find('link',rel='alternate')}
 assert set(alternates)=={'en','ar','x-default'},filename
 assert alternates[lang]==url and alternates['x-default']==alternates['en'],filename
 other=alternates['en' if lang=='ar' else 'ar'].removeprefix(site).lstrip('/')
 other+='index.html' if other.endswith('/') or not other else ''
 assert pages[other].find('link',rel='alternate',hreflang=lang,href=url),filename
 switch=[a for t,a in p.tags if t=='a' and 'data-language-link' in a]
 assert len(switch)==1 and site+switch[0]['href']==alternates['en' if lang=='ar' else 'ar'],filename
 assert len(p.find('h1'))==1,filename
 assert p.find('meta',property='og:url',content=url),filename
 assert not re.search(r'8:00|12:00|5:00|bqU3PonU9fr7E8uB9|openingHours|localStorage',text),filename
 # Generic video availability was explicitly confirmed on 4 October 2026.
 assert len(p.find('div',**{'class':'onlineOption'}))==1,filename
 assert len(p.find('a',href='/booking.html?mode=online&lang='+lang))==1,filename
 note='Outside Beirut? Video consultations are available.' if lang=='en' else 'تتوفّر استشارات عبر الفيديو للمرضى خارج بيروت.'
 assert note in text,filename
 assert len(p.find('script',src='/analytics.js'))==1,filename
 assert not p.find('script',src='https://www.googletagmanager.com/gtag/js?id=G-B46GF8Q2KX'),filename
 for tag,attrs in p.tags:
  links=[attrs[a] for a in ['href','src'] if a in attrs]
  if 'srcset' in attrs:links += [x.strip().split()[0] for x in attrs['srcset'].split(',')]
  for link in links:
   parsed=urlsplit(urljoin(url,link))
   if parsed.netloc!='drminhem.com':continue
   target=unquote(parsed.path).lstrip('/');target+='index.html' if not target or target.endswith('/') else ''
   assert (ROOT/target).is_file(),(filename,link,'missing file')
   if parsed.fragment and target in pages:assert parsed.fragment in pages[target].ids,(filename,link,'missing anchor')
 assert all(a.get('alt') for a in p.find('img')),filename
# Preserve baseline lines, allowing only the user's 4 October 2026 scope clarification.
# These literal replacements do not authorize any other credential or verification-link edits.
authorized_credential_replacements=[
 ('American Board–Certified (USA)','American Board–Certified in Internal Medicine (USA)'),
 ('American Board–Certified in the USA','American Board–Certified in Internal Medicine in the USA'),
 ('American Board–Certified, U.S.-trained','American Board–Certified in Internal Medicine, U.S.-trained'),
 ('American Board–Certified in the United States.','American Board–Certified in Internal Medicine in the United States.'),
 ('American Board of Internal Medicine — Board Certified (USA)','Internal Medicine — American Board of Internal Medicine (ABIM), Board Certified (USA)'),
 ('حاصل على البورد الأمريكي (ABIM)','حاصل على البورد الأمريكي في الطب الباطني (الولايات المتحدة)'),
]
original=subprocess.check_output(['git','show','5612dbd:index.html'],cwd=ROOT,text=True)
combined=files['index.html']+files['ar/index.html']
protected=[line.strip() for line in original.splitlines() if 'American Board' in line or 'البورد الأمريكي' in line]
for line in protected:
 expected=line.replace('Tayouneh and Sodeco','Sodeco and Tayouneh')
 for previous,approved in authorized_credential_replacements:expected=expected.replace(previous,approved)
 assert expected in combined,('Credential changed beyond the authorized wording',line)
for previous,approved in authorized_credential_replacements:
 assert previous not in combined,('Unscoped certification wording remains',previous)
 assert approved in combined,('Approved certification wording missing',approved)
assert len(protected)>10
sitemap=ET.parse(ROOT/'sitemap.xml');ns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
listed=[x.text for x in sitemap.findall('sm:url/sm:loc',ns)]
manifest_path=ROOT/'_content/generated.json'
manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'slugs':[]}
patient_manifest=json.loads((ROOT/'_content/patient_generated.json').read_text())
patient_slugs=patient_manifest['slugs'];directory_slug=patient_manifest['directory']
patient_items=[]
for content_file in ROOT.glob('_content/patient_*.json'):
 data=json.loads(content_file.read_text())
 if isinstance(data,list):patient_items.extend(data)
patient_content={item['slug']:item for item in patient_items}
assert len(patient_slugs)==len(set(patient_slugs)) and set(patient_slugs)==set(patient_content)
assert not set(patient_slugs)&set(manifest['slugs'])
page_dates=json.loads((ROOT/'_content/page_dates.json').read_text())
assert sorted(listed)==sorted(urls) and len(urls)==10+2*(len(manifest['slugs'])+len(patient_slugs)+1)
assert set(page_dates)=={url.removeprefix(site) for url in urls}
for path,dates in page_dates.items():
 assert 'last_modified' in dates,path
 assert all(date.fromisoformat(value).isoformat()==value for value in dates.values()),path
 if 'sources_checked' in dates:assert dates['sources_checked']<=dates['last_modified'],path
for slug in manifest['slugs']:
 for lang in ['en','ar']:
  name=('ar/' if lang=='ar' else '')+slug+'.html'
  page=pages[name]
  dates=page_dates['/'+name]
  assert page.find('p',**{'data-source-check':dates['sources_checked']}),name
  assert 'Draft for clinical review' not in files[name] and 'مسودة للمراجعة الطبية' not in files[name],name
  assert page.find('h2',id='sources'),name
  assert len(page.find('a',href='/booking.html?clinic=sodeco&lang='+lang))==2,name
  assert len(page.find('a',href='/booking.html?clinic=tayouneh&lang='+lang))==1,name
  assert not page.find('a',href='/booking.html?clinic=general&lang='+lang),name
  primary_label='Request a consultation at Sodeco Clinic' if lang=='en' else 'اطلب استشارة في عيادة سوديكو'
  assert '>'+primary_label+'</a>' in files[name],name
  assert page.find('p',**{'class':'clinicLocation'}),name
  raw=re.search(r'<script type="application/ld\+json">(.*?)</script>',files[name],re.S).group(1)
  schema=json.loads(raw)
  assert schema['@type']=='MedicalWebPage' and len(schema['citation'])>=2,name
  assert 'reviewedBy' not in schema and 'author' not in schema,name
  assert schema['dateModified']==dates['last_modified'],name
  assert pages[('ar/' if lang=='ar' else '')+'cancer-consultation.html'].find('a',href='/'+name),name
  if slug in {'lymphoma','leukemia','multiple-myeloma'}:
   assert pages[('ar/' if lang=='ar' else '')+'blood-cancer-consultation.html'].find('a',href='/'+name),name
# Patient guides are independently readable, sourced pages with discoverable navigation.
all_titles=[''.join(p.titles).strip() for name,p in pages.items() if name!='booking.html']
all_descriptions=[a['content'] for name,p in pages.items() if name!='booking.html' for a in p.find('meta',name='description')]
def region(text,tag,classname):
 match=re.search(r'<'+tag+r'\b[^>]*class="[^\"]*\b'+classname+r'\b[^\"]*"[^>]*>(.*?)</'+tag+r'>',text,re.S)
 assert match,('Missing region',classname)
 return Page(match[1])
def no_review_claims(value):
 if isinstance(value,dict):
  assert not {'author','reviewedBy'}&set(value),'Unrecorded authorship or clinical review'
  for child in value.values():no_review_claims(child)
 elif isinstance(value,list):
  for child in value:no_review_claims(child)
for lang in ['en','ar']:
 prefix='ar/' if lang=='ar' else '';directory=prefix+directory_slug+'.html'
 directory_page=pages[directory]
 # Keep a small homepage reading selection and appointment logistics; the directory holds all topics.
 home=files[prefix+'index.html']
 featured_match=re.search(r'<section\b[^>]*\bid="guides-'+lang+r'"[^>]*>(.*?)</section>',home,re.S)
 assert featured_match,('Missing homepage patient-guide section',lang)
 featured=Page(featured_match[1])
 all_guide_paths={'/'+prefix+slug+'.html' for slug in patient_slugs+manifest['slugs']}
 assert len(all_guide_paths)==22,(directory,'Expected complete 22-guide collection')
 featured_paths={'/'+prefix+slug+'.html' for slug in ['biopsy-cancer-spread','chemotherapy-benefits-risks','targeted-therapy','immunotherapy-candidacy']}
 assert {a['href'] for a in featured.find('a') if a.get('href') in all_guide_paths}==featured_paths,(lang,'Homepage must feature the four selected patient questions')
 assert featured.find('a',href='/'+directory),(lang,'Featured guides must lead to the full directory')
 faq_match=re.search(r'<section\b[^>]*\bid="faq-'+lang+r'"[^>]*>(.*?)</section>',home,re.S)
 assert faq_match,('Missing homepage practical FAQ',lang)
 faq=Page(faq_match[1])
 pairs=re.findall(r'<details\b[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>',faq_match[1],re.S)
 assert len(faq.find('details'))==len(pairs)==4,(lang,'Homepage FAQ must contain four practical questions')
 text_only=lambda fragment:' '.join(unescape(re.sub(r'<[^>]+>','',fragment)).split())
 assert not re.search(r'chemotherapy|كيميائي', ' '.join(text_only(question) for question,answer in pairs),re.I),(lang,'Treatment explanations belong in patient guides')
 home_schemas=[json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',home,re.S)]
 faq_schemas=[schema for schema in home_schemas if schema.get('@type')=='FAQPage']
 assert len(faq_schemas)==1 and len(faq_schemas[0]['mainEntity'])==4,(lang,'FAQ schema must match four visible questions')
 for (question,answer),schema in zip(pairs,faq_schemas[0]['mainEntity']):
  assert text_only(question)==schema['name'] and text_only(answer)==schema['acceptedAnswer']['text'],(lang,'FAQ schema differs from visible content')
 for name in [prefix+'index.html',prefix+'cancer-consultation.html',prefix+'blood-cancer-consultation.html']:
  assert pages[name].find('a',href='/'+directory),(name,'Missing patient-directory doorway')
 groups={item['category'] for item in patient_items}|{'cancer-types'}
 jumps=region(files[directory],'nav','directoryJump')
 assert {a['href'] for a in jumps.find('a')}=={'#'+group for group in groups},directory
 for group in groups:assert directory_page.find('h2',id=group),(directory,group)
 for slug in patient_slugs+manifest['slugs']:
  assert directory_page.find('a',href='/'+prefix+slug+'.html'),(directory,slug)
 assert {a['href'] for a in directory_page.find('a') if a.get('href') in all_guide_paths}==all_guide_paths,(directory,'Patient directory must retain every guide')
 for slug in patient_slugs+[directory_slug]:
  name=prefix+slug+'.html';page=pages[name];text=files[name];dates=page_dates['/'+name]
  title=''.join(page.titles).strip();descriptions=page.find('meta',name='description')
  assert title and all_titles.count(title)==1,(name,'Title must be distinct')
  assert len(descriptions)==1 and descriptions[0]['content'] and all_descriptions.count(descriptions[0]['content'])==1,(name,'Description must be distinct')
  assert all('noindex' not in a.get('content','').lower() for a in page.find('meta',name='robots')),name
  schemas=[json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)]
  assert len(schemas)==1,name
  schema=schemas[0];no_review_claims(schema)
  assert schema['dateModified']==dates['last_modified'] and schema['inLanguage']==lang,name
  assert schema['url']==site+'/'+name,name
  bookings=[a['href'] for a in page.find('a') if urlsplit(a.get('href','')).path=='/booking.html']
  assert bookings and parse_qs(urlsplit(bookings[0]).query)['clinic']==['sodeco'],name
  for href in bookings:
   query=parse_qs(urlsplit(href).query,keep_blank_values=True)
   is_clinic=set(query)=={'clinic','lang'} and query['clinic'] in [['sodeco'],['tayouneh']]
   is_video=set(query)=={'mode','lang'} and query['mode']==['online']
   assert (is_clinic or is_video) and query['lang']==[lang] and not urlsplit(href).fragment,(name,href)
  if slug==directory_slug:
   assert schema['@type']=='CollectionPage',name
   continue
  copy=patient_content[slug][lang]
  assert schema['@type']=='MedicalWebPage',name
  citations=schema['citation'];assert len(set(citations))>=2,name
  assert set(citations)=={source['url'] for source in patient_content[slug]['sources']},name
  source_links=region(text,'section','guideSources')
  assert {a['href'] for a in source_links.find('a')}==set(citations),name
  assert page.find('p',**{'data-source-check':dates['sources_checked']}),name
  toc=region(text,'nav','patientContents')
  expected_anchors={'#topic-'+section['id'] for section in copy['sections']}
  assert len(expected_anchors)>=3 and {a['href'] for a in toc.find('a')}==expected_anchors,name
  for anchor in expected_anchors:assert page.find('h2',id=anchor[1:]),(name,anchor)
  related=region(text,'ul','patientRelated')
  assert {a['href'] for a in related.find('a')}=={'/'+prefix+s+'.html' for s in copy['related']},name
  assert page.find('a',href='/'+directory),name
  if copy.get('urgent'):
   assert page.find('aside',**{'class':'patientUrgent'}),name
   assert text.index('class="patientUrgent"')<text.index('href="/booking.html'),(name,'Urgency must precede booking')
for entry in sitemap.findall('sm:url',ns):
 loc=entry.find('sm:loc',ns).text
 assert entry.find('sm:lastmod',ns).text==page_dates[loc.removeprefix(site)]['last_modified'],loc
 assert len(entry.findall('x:link',ns))==3,loc
robots=RobotFileParser();robots.parse((ROOT/'robots.txt').read_text().splitlines())
assert robots.can_fetch('Googlebot',site+'/booking.html'),'Booking noindex must be crawlable'
assert site+'/booking.html' not in listed
# Both homepage and Sodeco schema use the doctor's verified listing.
for filename in ['index.html','ar/index.html','sodeco.html','ar/sodeco.html']:
 assert '0xbce4d1d09856242c' in files[filename]
assert 'gtag(\'event\',\'appointment_booking\'' in files['booking.html']
print(f'PASS: {len(urls)} pages, canonical/hreflang reciprocity, sitemap, internal assets/anchors, JSON-LD, {len(patient_slugs)*2} sourced patient guides and bilingual directory, scheduling/maps, and {len(protected)} protected American Board wording checks.')
