/* Run with NODE_PATH pointing to an installed Playwright package and the preview on port 8765. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = 'http://127.0.0.1:8765';
const evidence = path.resolve(__dirname, '../../evidence');
const layoutViewports=[{width:1365,height:900},{width:390,height:844},{width:320,height:844},{width:768,height:1024},{width:1440,height:1000}];
const screenshotMatrix=[];
const sharedLayouts=[['home',''],['clinic','sodeco.html'],['consultation','cancer-consultation.html'],['condition-guide','breast-cancer.html'],['patient-guide','immunotherapy-candidacy.html'],['patient-directory','patient-guides.html']];
for(const [layout,filename] of sharedLayouts)for(const language of ['en','ar'])for(const viewport of [{name:'phone',width:390,height:844},{name:'desktop',width:1440,height:1000}]){
 const route=(language==='ar'?'/ar/':'/')+filename;const file='responsive-'+layout+'-'+language+'-'+viewport.name+'.png';
 screenshotMatrix.push({layout,language,route,viewport:viewport.name,width:viewport.width,height:viewport.height,file});
}
const routes = ['/', '/ar/', '/sodeco.html', '/ar/sodeco.html', '/tayouneh.html', '/ar/tayouneh.html', '/cancer-consultation.html', '/ar/cancer-consultation.html', '/blood-cancer-consultation.html', '/ar/blood-cancer-consultation.html'];
const manifestPath=path.resolve(__dirname,'../_content/generated.json');
const guideSlugs=fs.existsSync(manifestPath)?JSON.parse(fs.readFileSync(manifestPath,'utf8')).slugs:[];
for(const slug of guideSlugs) routes.push('/'+slug+'.html','/ar/'+slug+'.html');
const patientManifest=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../_content/patient_generated.json'),'utf8'));
const patientSlugs=patientManifest.slugs;
const patientRoutes=patientSlugs.flatMap(slug=>['/'+slug+'.html','/ar/'+slug+'.html']);
const directoryRoutes=['/'+patientManifest.directory+'.html','/ar/'+patientManifest.directory+'.html'];
routes.push(...patientRoutes,...directoryRoutes);
assert.equal(new Set(routes).size,routes.length,'Duplicate verification routes');
// Check button-like targets and navigation controls, not ordinary links within prose.
async function checkVisibleControls(page,route,width,scope=null){
 const report=await page.evaluate(scope=>{
  const root=scope?document.querySelector(scope):document;
  const selector=scope?'a,button':'a.btn,a.button,a.guideLink,a.scopeAction,a.chip[href],[data-language-link],button,summary,.patientContents a,.patientRelated a,.directoryJump a,.patientDiscuss,.patientBack,.mobileMenu a';
  const largeTargets='a.btn,a.button,a.guideLink,[data-language-link],button,summary,.patientContents a,.patientRelated a,.directoryJump a,.patientDiscuss,.patientBack,.mobileMenu a';
  const issues=[];let checked=0;let inViewport=0;
  for(const el of root.querySelectorAll(selector)){
   if(!el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))continue;
   const rect=el.getBoundingClientRect();if(!rect.width||!rect.height)continue;
   checked++;
   const label=(el.getAttribute('aria-label')||el.textContent).trim().replace(/\s+/g,' ').slice(0,100);
   const fail=reason=>issues.push({label,reason,width:Math.round(rect.width),height:Math.round(rect.height)});
   if(rect.left < -1||rect.right > innerWidth+1)fail('Control extends outside viewport horizontally');
   const minimum=el.matches(largeTargets)?44:24;
   if(rect.width<minimum-1||rect.height<minimum-1)fail('Standalone target smaller than '+minimum+'px');
   const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
   while(walker.nextNode()){
    const node=walker.currentNode;if(!node.textContent.trim()||!node.parentElement.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))continue;
    const range=document.createRange();range.selectNodeContents(node);
    if([...range.getClientRects()].some(r=>r.left<rect.left-2||r.right>rect.right+2||r.top<rect.top-2||r.bottom>rect.bottom+2)){
     fail('Control label is clipped or extends outside its target');break;
    }
   }
   for(let ancestor=el.parentElement;ancestor&&ancestor!==document.body;ancestor=ancestor.parentElement){
    const style=getComputedStyle(ancestor);const bounds=ancestor.getBoundingClientRect();
    if((['hidden','clip'].includes(style.overflowX)&&(rect.left<bounds.left-2||rect.right>bounds.right+2))||(['hidden','clip'].includes(style.overflowY)&&(rect.top<bounds.top-2||rect.bottom>bounds.bottom+2))){
     fail('Control is clipped by an ancestor');break;
    }
   }
   if(rect.top>=0&&rect.bottom<=innerHeight&&getComputedStyle(el).pointerEvents!=='none'){
    inViewport++;
    const hit=document.elementFromPoint(rect.left+rect.width/2,rect.top+rect.height/2);
    if(hit&&!el.contains(hit))fail('Control center is covered by another element');
   }
  }
  return {checked,inViewport,issues};
 },scope);
 assert.deepEqual(report.issues,[],route+' visible controls at '+width+'px');
 return {width,checked:report.checked,inViewport:report.inViewport};
}
// Activate a contents link with the keyboard and ensure its target is not hidden by the sticky navigation.
async function checkKeyboardAnchor(page,selector,route){
 const links=page.locator(selector);assert.ok(await links.count()>1,route+' anchor navigation');
 await links.first().focus();await page.keyboard.press('Tab');
 assert.equal(await links.nth(1).evaluate(el=>el===document.activeElement),true,route+' sequential keyboard focus');
 assert.equal(await links.nth(1).evaluate(el=>el.matches(':focus-visible')&&getComputedStyle(el).outlineStyle!=='none'&&parseFloat(getComputedStyle(el).outlineWidth)>0),true,route+' visible keyboard focus');
 const href=await links.nth(1).getAttribute('href');
 await page.keyboard.press('Enter');
 assert.equal(new URL(page.url()).hash,href,route+' keyboard anchor activation');
 const geometry=await page.locator(href).evaluate(el=>({top:el.getBoundingClientRect().top,bottom:el.getBoundingClientRect().bottom,navBottom:document.querySelector('.siteNav').getBoundingClientRect().bottom,height:innerHeight}));
 assert.ok(geometry.top>=geometry.navBottom-1&&geometry.bottom<=geometry.height,route+' anchor target visible below navigation');
}
(async () => {
 fs.mkdirSync(evidence,{recursive:true});
 const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context = await browser.newContext({viewport:{width:1365,height:900}, reducedMotion:'reduce'});
 const errors=[]; const network=[];
 context.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
 await context.route(/https:\/\/(?:www\.)?(?:wa\.me|api\.whatsapp\.com|www\.googletagmanager\.com|www\.google-analytics\.com).*$/, route => route.abort());
 context.on('request',r=>network.push(r.url()));
 const page=await context.newPage(); const results=[];const headerBreakpointChecks=[];
 // Save representative first screens before assertions so reviewers can inspect them even if a later route fails.
 for(const shot of screenshotMatrix){
  await page.setViewportSize({width:shot.width,height:shot.height});await page.goto(base+shot.route);await page.evaluate(()=>document.fonts.ready);
  await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.filter(i=>{const r=i.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0}).map(i=>i.decode().catch(()=>{}))));
  await page.screenshot({path:path.join(evidence,shot.file),fullPage:false});
 }
 fs.writeFileSync(path.join(evidence,'responsive-screenshot-matrix.json'),JSON.stringify(screenshotMatrix,null,2));
 console.log('Saved 24 bilingual phone/desktop screenshots in responsive-screenshot-matrix.json.');
 // Test both sides of header layout changes; these widths are easy to miss in device presets.
 for(const route of ['/','/ar/'])for(const width of [980,981,1199,1200,1239,1240,1399,1400]){
  await page.setViewportSize({width,height:1000});await page.goto(base+route);await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,route+' header breakpoint overflow '+width);
  headerBreakpointChecks.push({route,...await checkVisibleControls(page,route,width,'.topbar')});
 }
 console.log('PASS: bilingual header transition checks at 980 / 981 / 1199 / 1200 / 1239 / 1240 / 1399 / 1400px.');
 await page.setViewportSize({width:1365,height:900});
 for (const route of routes) {
  const response=await page.goto(base+route); assert.equal(response.status(),200,route);
  await page.evaluate(()=>document.fonts.ready);
  const lang=route.startsWith('/ar/')?'ar':'en';
  assert.equal(await page.getAttribute('html','lang'),lang);
  assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('h1').isVisible(),true);
  assert.ok((await page.locator('body').innerText()).length>500);
  assert.equal(await page.locator('script[src*=googletagmanager]').count(),0);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,route+' desktop overflow');
  const controlChecks=[await checkVisibleControls(page,route,1365)];
  await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(i=>{i.loading='eager';return i.decode().catch(()=>{});})));
  assert.deepEqual(await page.locator('img').evaluateAll(imgs=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)),[],route+' images');
  const alternate=await page.locator('[data-language-link]').getAttribute('href');
  await page.locator('[data-language-link]').click();
  assert.equal(new URL(page.url()).pathname,alternate);
  assert.equal(await page.getAttribute('html','lang'),lang==='ar'?'en':'ar');
  for (const viewport of layoutViewports.slice(1)) {
   await page.setViewportSize(viewport);await page.goto(base+route);await page.evaluate(()=>document.fonts.ready);
   const {width}=viewport;
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,route+' layout overflow '+width);
   assert.equal(await page.locator('h1').isVisible(),true);
   controlChecks.push(await checkVisibleControls(page,route,width));
  }
  results.push({route,status:response.status(),language:lang,languageSwitch:true,mobileWidths:[390,320],viewportWidths:layoutViewports.map(v=>v.width),overflow:false,visibleControls:controlChecks});
  await page.setViewportSize({width:1365,height:900});
 }
 // Stable routes take precedence over old saved preference.
 await page.goto(base+'/');await page.evaluate(()=>localStorage.setItem('site_lang','ar'));await page.reload();assert.equal(await page.getAttribute('html','lang'),'en');
 for(const [from,to] of [['/?lang=ar','/ar/'],['/#contact-ar','/ar/#contact-ar'],['/sodeco.html?lang=ar','/ar/sodeco.html'],['/ar/tayouneh.html?lang=en','/tayouneh.html']]){
  await page.goto(base+from);await page.waitForURL(base+to);assert.equal(page.url(),base+to);
 }
 // Malformed incoming fragments do not stop menus / page enhancements.
 await page.goto(base+'/#%zz');assert.equal(await page.locator('h1').isVisible(),true);
 // English and Arabic mobile menu controls work, and Escape restores focus.
 await page.setViewportSize({width:390,height:844});
 for(const lang of ['en','ar']) {
  await page.goto(base+(lang==='ar'?'/ar/':'/'));
  const id=lang==='ar'?'#menuBtnAr':'#menuBtn';
  await page.locator(id).click();assert.equal(await page.locator(id).getAttribute('aria-expanded'),'true');
  await page.keyboard.press('Escape');assert.equal(await page.locator(id).getAttribute('aria-expanded'),'false');
  assert.equal(await page.locator(id).evaluate(e=>e===document.activeElement),true);
 }
 // Certificate dialog still opens and closes in both languages.
 for(const lang of ['en','ar']) {
  await page.goto(base+(lang==='ar'?'/ar/':'/'));
  await page.locator('[data-certificate]').first().evaluate(el=>{let p=el.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}});
  await page.locator('[data-certificate]').first().click();assert.equal(await page.locator('#certificate-dialog').evaluate(e=>e.open),true);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#certificate-dialog').evaluate(e=>e.open),false);
 }
 // Patient content remains visible when the enhancement script fails.
 const resilient=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'no-preference'});
 await resilient.route('**/site.js',route=>route.abort());
 const rp=await resilient.newPage();
 for(const lang of ['en','ar']){
  await rp.goto(base+(lang==='ar'?'/ar/':'/'));
  assert.equal(await rp.locator('.hero h1').evaluate(el=>getComputedStyle(el.closest('.reveal')).opacity),'1');
  assert.equal(await rp.locator('.clinicCard').first().evaluate(el=>getComputedStyle(el).opacity),'1');
  const sections=await rp.locator('main > section').evaluateAll(els=>els.map(el=>el.id));
  assert.ok(sections.indexOf('care-'+lang)<sections.indexOf('contact-'+lang));
  assert.ok(sections.indexOf('contact-'+lang)<sections.indexOf('recognition-'+lang));
  assert.equal(new URL(await rp.locator('.hero .ctaRow a[href^="/booking.html"]').getAttribute('href'),base).searchParams.get('clinic'),'sodeco');
 }
 await resilient.close();
 // On pages with portraits, the mobile appointment action still precedes the portrait.
 for(const route of routes.filter(r=>r!=='/'&&r!=='/ar/')){
  await page.goto(base+route);
  if(!await page.locator('.hero .portrait').count())continue;
  const boxes=await page.locator('.hero').evaluate(hero=>({action:hero.querySelector('a[href^="/booking.html"]').getBoundingClientRect().top,portrait:hero.querySelector('.portrait').getBoundingClientRect().top}));
  assert.ok(boxes.action<boxes.portrait,route+' mobile action order');
 }
 // Patient guides put readable answers and urgent advice ahead of appointment requests.
 for(const route of patientRoutes){
  await page.goto(base+route);
  assert.equal(await page.locator('.hero .lead').isVisible(),true,route+' answer visible');
  assert.equal(await page.locator('.patientContents').isVisible(),true,route+' contents visible');
  for(const href of await page.locator('.patientContents a').evaluateAll(as=>as.map(a=>a.getAttribute('href')))){
   assert.ok(href.startsWith('#topic-'),route+' contents anchor');
   assert.equal(await page.locator(href).count(),1,route+' unique contents target');
   await page.locator('.patientContents a[href="'+href+'"]').click();
   assert.equal(new URL(page.url()).hash,href,route+' contents link');
   assert.equal(await page.locator(href).isVisible(),true,route+' contents target visible');
  }
  if(await page.locator('.patientUrgent').count()){
   assert.equal(await page.locator('.patientUrgent').isVisible(),true,route+' urgent advice visible');
   assert.equal(await page.locator('.patientUrgent').evaluate(urgent=>{
    const booking=document.querySelector('a[href^="/booking.html"]');
    return !!(urgent.compareDocumentPosition(booking)&Node.DOCUMENT_POSITION_FOLLOWING)&&urgent.getBoundingClientRect().bottom<=booking.getBoundingClientRect().top;
   }),true,route+' urgent advice before appointment action');
  }
  await checkKeyboardAnchor(page,'.patientContents a',route);
 }
 for(const route of directoryRoutes){
  await page.goto(base+route);
  const prefix=route.startsWith('/ar/')?'/ar/':'/';
  assert.equal(await page.locator('.patientGroup').count(),5,route+' grouped directory');
  for(const slug of [...patientSlugs,...guideSlugs]){
   const link=page.locator('.patientGroup a[href="'+prefix+slug+'.html"]');
   assert.equal(await link.count(),1,route+' directory guide '+slug);
   assert.equal(await link.isVisible(),true,route+' visible guide '+slug);
  }
  for(const href of await page.locator('.directoryJump a').evaluateAll(as=>as.map(a=>a.getAttribute('href')))){
   await page.locator('.directoryJump a[href="'+href+'"]').click();
   assert.equal(new URL(page.url()).hash,href,route+' directory jump');
   assert.equal(await page.locator(href).isVisible(),true,route+' directory target');
  }
  await checkKeyboardAnchor(page,'.directoryJump a',route);
 }
 // Every appointment href uses only controlled clinic/language values.
 for(const route of routes){await page.goto(base+route);for(const href of await page.locator('a[href^="/booking.html"]').evaluateAll(as=>as.map(a=>a.getAttribute('href')))){
   const u=new URL(href,base);assert.deepEqual([...u.searchParams.keys()],['clinic','lang']);assert.ok(['general','sodeco','tayouneh'].includes(u.searchParams.get('clinic')));assert.equal(u.searchParams.get('lang'),route.startsWith('/ar/')?'ar':'en');
 }}
 // Inspect WhatsApp intent event before redirect without contacting WhatsApp.
 await page.addInitScript(()=>{const original=window.setTimeout;window.setTimeout=(fn,delay,...args)=>delay===1800?0:original(fn,delay,...args)});
 await page.goto(base+'/booking.html?clinic=sodeco&lang=ar');
 const events=await page.evaluate(()=>window.dataLayer.map(a=>Array.from(a)).filter(a=>a[0]==='event'));
 assert.equal(events.length,1);assert.equal(events[0][1],'appointment_booking');assert.equal(events[0][2].clinic_location,'sodeco');assert.equal(events[0][2].site_language,'ar');
 assert.equal(await page.locator('#backLink').getAttribute('href'),'/ar/');
 assert.match(await page.locator('#continueLink').getAttribute('href'),/^https:\/\/wa\.me\/96181902903\?text=/);
 await page.goto(base+'/booking.html?clinic=unknown&lang=ar&preview=1');assert.equal(await page.evaluate(()=>dataLayer.filter(a=>a[0]==='event').length),0);
 assert.ok(!(await page.locator('#continueLink').getAttribute('href')).includes('unknown'));
 // Sitemap is accessible and every declared page returned 200 above.
 assert.equal((await context.request.get(base+'/sitemap.xml')).status(),200);
 assert.equal((await context.request.get(base+'/robots.txt')).status(),200);
 const shots=[['/','home-en-desktop.png',1365,900,false],['/ar/','home-ar-mobile.png',390,844,false],['/sodeco.html','sodeco-en-desktop.png',1365,1000,true],['/ar/sodeco.html','sodeco-ar-mobile.png',390,844,true],['/cancer-consultation.html','cancer-en-desktop.png',1365,900,true],['/ar/cancer-consultation.html','cancer-ar-mobile.png',390,844,true],['/blood-cancer-consultation.html','blood-cancer-en-mobile.png',390,844,true],['/ar/blood-cancer-consultation.html','blood-cancer-ar-mobile.png',390,844,true]];
 for(const slug of guideSlugs){shots.push(['/'+slug+'.html',slug+'-en-desktop.png',1365,900,true],['/ar/'+slug+'.html',slug+'-ar-mobile.png',390,844,true]);}
 for(const slug of [...patientSlugs,patientManifest.directory]){shots.push(['/'+slug+'.html',slug+'-en-desktop.png',1365,900,true],['/ar/'+slug+'.html',slug+'-ar-mobile.png',390,844,true]);}
 for(const [route,name,width,height,fullPage] of shots){await page.setViewportSize({width,height});await page.goto(base+route);await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(evidence,name),fullPage});}
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await nojs.newPage();
 for(const route of routes){
  assert.equal((await np.goto(base+route)).status(),200);assert.equal(await np.locator('h1').isVisible(),true);
  if(patientRoutes.includes(route)){
   assert.equal(await np.locator('.hero .lead').isVisible(),true,route+' no-JS answer');
   assert.equal(await np.locator('.patientContents').isVisible(),true,route+' no-JS contents');
   assert.equal(await np.locator('.guideSources').isVisible(),true,route+' no-JS sources');
   const href=await np.locator('.patientContents a').first().getAttribute('href');
   await np.locator('.patientContents a').first().click();assert.equal(new URL(np.url()).hash,href);
   assert.equal(await np.locator(href).isVisible(),true,route+' no-JS anchor target');
   if(await np.locator('.patientUrgent').count())assert.equal(await np.locator('.patientUrgent').isVisible(),true,route+' no-JS urgent advice');
  }
  if(directoryRoutes.includes(route)){
   const prefix=route.startsWith('/ar/')?'/ar/':'/';
   const links=np.locator('.patientGroup .guideLink');assert.equal(await links.count(),patientSlugs.length+guideSlugs.length,route+' no-JS directory');
   const href=prefix+patientSlugs[0]+'.html';await np.locator('.patientGroup a[href="'+href+'"]').click();
   assert.equal(new URL(np.url()).pathname,href);assert.equal(await np.locator('.hero .lead').isVisible(),true);
   await np.goto(base+route);
  }
  const lang=await np.getAttribute('html','lang');await np.locator('[data-language-link]').click();assert.notEqual(await np.getAttribute('html','lang'),lang);
 }
 assert.deepEqual(errors,[]);assert.equal(network.some(u=>/googletagmanager|google-analytics|wa\.me/.test(u)),false);
 fs.writeFileSync(path.join(evidence,'browser-results.json'),JSON.stringify({results,viewportWidths:layoutViewports.map(v=>v.width),headerBreakpointChecks,visibleControlClippingAndSize:true,screenshotMatrix,consoleErrors:errors,externalAnalyticsOrWhatsAppRequests:0,noJavaScript:routes.length,legacyLinks:true,mobileMenus:true,certificateDialogs:true,bookingIntent:true,scriptFailureVisible:true,mobileActionBeforePortrait:true,patientGuides:{routes:patientRoutes.length,contentsAnchors:true,keyboardFocus:true,urgentAdviceBeforeBooking:true,noJavaScript:true},patientDirectory:{routes:directoryRoutes.length,groupLinks:true,keyboardFocus:true,noJavaScript:true},screenshots:[...shots.map(s=>s[1]),...screenshotMatrix.map(s=>s.file)]},null,2));
 console.log(`PASS: ${routes.length} pages × 320 / 390 / 768 / 1365 / 1440px; visible control sizes/clipping; ${routes.length} no-JS language switches; legacy links, menus, certificates, appointment intent, sitemap/robots, no page errors and no analytics/WhatsApp requests.`);
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
