/* Development-only browser acceptance check; no network or provider API required. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const path=require('node:path'),fs=require('node:fs');
(async()=>{
 const root=path.join(__dirname,'materials'),shots=path.join(root,'screenshots');fs.mkdirSync(shots,{recursive:true});
 const browser=await chromium.launch({headless:true});const errors=[],requests=[];
 const page=await browser.newPage({viewport:{width:1920,height:1080}});
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith('file:'))requests.push(r.url());});
 await page.goto('file://'+path.join(root,'replay.html'));
 for(let scene=0;scene<6;scene++){
  await page.locator('#scenes button').nth(scene).click();
  for(let step=0;step<4;step++){
   if(step)await page.keyboard.press('ArrowRight');
   await page.screenshot({path:path.join(shots,`${scene+1}-${step}.png`)});
   if(await page.locator('.panel').evaluateAll(es=>es.some(e=>e.scrollHeight>e.clientHeight+2)))throw Error(`Overflow scene ${scene}, step ${step}`);
  }
 }
 await page.locator('#scenes button').nth(0).click();
 if((await page.locator('#right').innerText()).includes('退出码'))throw Error('Answer not reset');
 await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowLeft');
 if(!(await page.locator('#leftTitle').innerText()).includes('先预测'))throw Error('Backward navigation failed');
 for(const [width,height,name] of [[1280,720,'viewport-1280'],[390,844,'viewport-phone']]){
  await page.setViewportSize({width,height});await page.screenshot({path:path.join(shots,name+'.png')});
 }
 await browser.close();const result={scenes:6,states:24,answer_reset:true,keyboard_navigation:true,network_requests:requests,console_errors:errors,viewports:['1920x1080','1280x720','390x844']};
 fs.writeFileSync(path.join(root,'browser-check.json'),JSON.stringify(result,null,2)+'\n');
 if(errors.length||requests.length)throw Error('Unexpected errors or network');console.log(result);
})().catch(e=>{console.error(e.message);process.exitCode=1;});
