/* Development-only recording utility. Runtime course remains dependency-free. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const path=require('node:path');const fs=require('node:fs');
(async()=>{
 const root=path.join(__dirname,'materials');const out=path.join(root,'clips');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true});
 for(const [index,name] of [[0,'01-normal'],[1,'02-no-evidence'],[2,'03-changed-question'],[3,'04-real-failure']]){
  const context=await browser.newContext({viewport:{width:1920,height:1080},recordVideo:{dir:out,size:{width:1920,height:1080}}});
  const page=await context.newPage();await page.goto('file://'+path.join(root,'replay.html'));
  await page.locator('#scenes button').nth(index).click();await page.mouse.move(1780,1010);
  for(let step=0;step<4;step++){if(step)await page.keyboard.press('ArrowRight');await page.waitForTimeout(step===3?9000:5000);}
  const video=page.video();const temporary=await video.path();await context.close();await video.saveAs(path.join(out,name+'.webm'));if(temporary!==path.join(out,name+'.webm'))fs.unlinkSync(temporary);
  console.log('Recorded '+name+' (silent historical replay)');
 }
 await browser.close();
})().catch(e=>{console.error(e.message);process.exitCode=1;});
