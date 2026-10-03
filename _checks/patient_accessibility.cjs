/* Check the new reading templates, using the locally available axe installation. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const manifest = require('../_content/patient_generated.json');
const evidence = path.resolve(__dirname, '../../evidence');
const axePath = process.env.AXE_PATH;
if (!axePath) throw new Error('Set AXE_PATH to a local axe-core/axe.min.js installation.');
(async () => {
 const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context = await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
 await context.route(/https:\/\/(?:www\.)?(?:wa\.me|api\.whatsapp\.com|www\.googletagmanager\.com|www\.google-analytics\.com).*$/, r => r.abort());
 const page = await context.newPage();
 const results=[];
 for (const slug of [manifest.directory,...manifest.slugs]) {
  for(const lang of ['en','ar']) {
   const route=(lang==='ar'?'/ar/':'/')+slug+'.html';
   await page.goto('http://127.0.0.1:8765'+route);
   await page.evaluate(()=>document.fonts.ready);
   await page.addScriptTag({path:axePath});
   const result=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
   assert.equal(await page.locator('main h1').count(),1,route+' main includes title and answer');
   await page.keyboard.press('Tab');
   assert.equal(await page.locator('.skipLink').evaluate(el=>el===document.activeElement),true,route+' skip link first');
   await page.keyboard.press('Enter');
   assert.equal(await page.locator('main').evaluate(el=>el===document.activeElement),true,route+' skip target focus');
   results.push({route,violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),incomplete:result.incomplete.map(v=>v.id)});
   if(['patient-guides','biopsy-cancer-spread','chemotherapy-benefits-risks','immunotherapy-candidacy','nutrition-during-cancer-treatment','targeted-therapy','cancer-genetic-testing'].includes(slug)) {
    await page.goto('http://127.0.0.1:8765'+route);await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:path.join(evidence,slug+'-'+lang+'-mobile-viewport.png')});
    await page.screenshot({path:path.join(evidence,slug+'-'+lang+'-full.png'),fullPage:true});
   }
  }
 }
 await page.setViewportSize({width:1365,height:900});
 for (const lang of ['en','ar']) {
  await page.goto('http://127.0.0.1:8765/'+(lang==='ar'?'ar/':'')+'patient-guides.html');
  await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(evidence,'patient-guides-'+lang+'-desktop.png')});
 }
 fs.writeFileSync(path.join(evidence,'patient-accessibility.json'),JSON.stringify(results,null,2));
 assert.equal(results.filter(r=>r.violations.length).length,0,'See patient-accessibility.json');
 console.log(`PASS: ${results.length} new pages, automated WCAG checks, main landmark and keyboard skip links.`);
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
