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
