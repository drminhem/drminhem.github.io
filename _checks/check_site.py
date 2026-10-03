"""Regression checks for static pages. Run from the repository: python3 _checks/check_site.py."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin, unquote
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
 assert 'video consultation' not in text.lower() and 'استشارة فيديو' not in text,filename
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
# Preserve every complete original source line containing American Board wording, in either language.
original=subprocess.check_output(['git','show','5612dbd:index.html'],cwd=ROOT,text=True)
combined=files['index.html']+files['ar/index.html']
protected=[line.strip() for line in original.splitlines() if 'American Board' in line or 'البورد الأمريكي' in line]
for line in protected:assert line in combined,('Credential changed',line)
assert len(protected)>10
sitemap=ET.parse(ROOT/'sitemap.xml');ns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
listed=[x.text for x in sitemap.findall('sm:url/sm:loc',ns)]
assert sorted(listed)==sorted(urls) and len(urls)==10
for entry in sitemap.findall('sm:url',ns):
 loc=entry.find('sm:loc',ns).text
 assert len(entry.findall('x:link',ns))==3,loc
# Both homepage and Sodeco schema use the doctor's verified listing.
for filename in ['index.html','ar/index.html','sodeco.html','ar/sodeco.html']:
 assert '0xbce4d1d09856242c' in files[filename]
assert 'gtag(\'event\',\'appointment_booking\'' in files['booking.html']
print(f'PASS: {len(urls)} pages, canonical/hreflang reciprocity, sitemap, internal assets/anchors, JSON-LD, scheduling/maps, and {len(protected)} exact American Board source lines.')
