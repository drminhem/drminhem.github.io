// Isolated checks: no requests leave this process.
const fs=require('node:fs');const vm=require('node:vm');const assert=require('node:assert/strict');
const code=fs.readFileSync('analytics.js','utf8');
function analytics(hostname,search=''){
 const loaded=[];const window={location:{hostname,search,origin:'https://'+hostname,pathname:'/booking.html'}};
 const document={referrer:'https://example.org/private-path?query=QA_MARKER',title:'Opening WhatsApp',createElement:()=>({}),head:{appendChild:x=>loaded.push(x)}};
 const sandbox=Object.assign(window,{window,document,URL,URLSearchParams,Date});vm.createContext(sandbox);vm.runInContext(code,sandbox);return {loaded,events:window.dataLayer};
}
const production=analytics('drminhem.com','?clinic=sodeco&notes=QA_MARKER#QA_MARKER');
assert.equal(production.loaded.length,1);assert.equal(production.events.filter(e=>e[0]==='config').length,1);
const config=production.events.find(e=>e[0]==='config')[2];assert.equal(config.page_location,'https://drminhem.com/booking.html');assert.equal(config.page_referrer,'https://example.org/');assert.ok(!JSON.stringify(production.events).includes('QA_MARKER'));
assert.equal(analytics('127.0.0.1').loaded.length,0);assert.equal(analytics('drminhem.com','?preview=1').loaded.length,0);
const language=fs.readFileSync('language.js','utf8');
for(const [input,expected] of [['https://drminhem.com/?lang=ar&notes=QA_MARKER','/ar/'],['https://drminhem.com/#contact-ar','/ar/#contact-ar'],['https://drminhem.com/ar/?lang=en#care-ar','/#care-en'],['https://drminhem.com/?lang=ar#QA_MARKER','/ar/'],['https://drminhem.com/ar/',null],['https://drminhem.com/sodeco.html',null]]){
 let replaced=null;const location=new URL(input);location.href=input;location.replace=x=>replaced=x;
 vm.runInNewContext(language,{window:{location},URL});assert.equal(replaced,expected);
}
console.log('PASS: one GA4 property initialization, sanitized page/referrer context, no local/preview collection, safe legacy language routing.');

// Evaluate the actual booking script with a tiny DOM and no network or real navigation.
const bookingHtml=fs.readFileSync('booking.html','utf8');
const bookingScripts=[...bookingHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(bookingScripts.length,1,'One booking script');
function booking(search){
 const nodes=Object.fromEntries(['title','message','clinicName','continueLink','backLink'].map(id=>[id,{textContent:'',innerHTML:'',href:''}]));
 const events=[];const redirects=[];const timers=[];
 const document={documentElement:{},title:'',getElementById:id=>nodes[id]};
 const window={location:{search,replace:url=>redirects.push(url)},setTimeout:(fn,delay)=>timers.push({fn,delay})};
 vm.runInNewContext(bookingScripts[0][1],{window,document,URLSearchParams,encodeURIComponent,gtag:(...args)=>events.push(args)});
 return {nodes,document,events,redirects,timers};
}
const drafts={
 en:{online:'Hello Dr. Minhem, I would like to request a video consultation.',sodeco:'Hello Dr. Minhem, I would like to book an appointment at the Sodeco clinic.',tayouneh:'Hello Dr. Minhem, I would like to book an appointment at the Tayouneh clinic.',general:'Hello Dr. Minhem, I would like to book an appointment.'},
 ar:{online:'مرحباً دكتور منعم، أودّ طلب موعد لاستشارة عبر الفيديو.',sodeco:'مرحباً دكتور منعم، أودّ حجز موعد في عيادة سوديكو.',tayouneh:'مرحباً دكتور منعم، أودّ حجز موعد في عيادة الطيونة.',general:'مرحباً دكتور منعم، أودّ حجز موعد.'}
};
const safeBookingCases=[
 {query:'mode=online',mode:'online',clinic:'general',draft:'online'},
 {query:'mode=online&clinic=sodeco',mode:'online',clinic:'general',draft:'online'},
 {query:'clinic=sodeco',mode:'clinic',clinic:'sodeco',draft:'sodeco'},
 {query:'clinic=tayouneh',mode:'clinic',clinic:'tayouneh',draft:'tayouneh'},
 {query:'mode=unknown&clinic=sodeco',mode:'clinic',clinic:'sodeco',draft:'sodeco'},
 {query:'mode=%3Cscript%3EQA_MARKER%3C%2Fscript%3E&clinic=QA_MARKER&notes=QA_MARKER',mode:'clinic',clinic:'general',draft:'general'},
 {query:'',mode:'clinic',clinic:'general',draft:'general'}
];
for(const lang of ['en','ar'])for(const test of safeBookingCases)for(const preview of [false,true]){
 const state=booking('?'+test.query+'&lang='+lang+(preview?'&preview=1':'')+'&message=QA_MARKER');
 const link=new URL(state.nodes.continueLink.href);
 assert.equal(link.origin,'https://wa.me');assert.equal(link.pathname,'/96181902903');
 assert.deepEqual([...link.searchParams.keys()],['text']);assert.equal(link.searchParams.get('text'),drafts[lang][test.draft]);
 assert.equal(state.document.documentElement.lang,lang);assert.equal(state.document.documentElement.dir,lang==='ar'?'rtl':'ltr');
 assert.equal(state.nodes.backLink.href,lang==='ar'?'/ar/':'/');
 assert.ok(!JSON.stringify({nodes:state.nodes,events:state.events}).includes('QA_MARKER'),'Incoming free text stays out of DOM, draft and analytics');
 if(test.mode==='online'){
  assert.equal(state.nodes.message.textContent,lang==='ar'?'رسالتك لطلب موعد لاستشارة عبر الفيديو جاهزة للإرسال.':'Your request for a video consultation is ready.');
  assert.doesNotMatch(state.nodes.message.textContent,/Sodeco|Tayouneh|سوديكو|الطيونة/);
 }
 assert.deepEqual(state.redirects,[],'No immediate redirect before callback or fallback');
 if(preview){assert.deepEqual(state.events,[]);assert.deepEqual(state.timers,[]);continue;}
 assert.equal(state.events.length,1);assert.deepEqual(state.events[0].slice(0,2),['event','appointment_booking']);
 const event=state.events[0][2];
 assert.deepEqual(Object.keys(event).sort(),['booking_channel','clinic_location','consultation_mode','event_callback','site_language','transport_type']);
 assert.equal(event.consultation_mode,test.mode);assert.equal(event.clinic_location,test.clinic);assert.equal(event.site_language,lang);assert.equal(event.booking_channel,'whatsapp');
 assert.equal(state.timers.length,1);assert.equal(state.timers[0].delay,1800);
 // Either analytics callback or timeout opens the same fixed draft once, in either order.
 if(lang==='en'){event.event_callback();state.timers[0].fn();}else{state.timers[0].fn();event.event_callback();}
 assert.deepEqual(state.redirects,[state.nodes.continueLink.href]);
}
const unknownLanguage=booking('?mode=online&lang=QA_MARKER&preview=1');
assert.equal(unknownLanguage.document.documentElement.lang,'en');
assert.equal(new URL(unknownLanguage.nodes.continueLink.href).searchParams.get('text'),drafts.en.online);
console.log('PASS: clinic and video-consultation drafts in both languages, allowlisted modes, safe fallbacks, one intent event/redirect, and preview with no event or redirect.');
