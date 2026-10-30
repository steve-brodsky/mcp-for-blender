const { chromium } = require(process.argv[2]);
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const artifactDir = path.resolve(root, '../../output/playwright');
  fs.mkdirSync(artifactDir, {recursive:true});
  fs.writeFileSync(path.join(artifactDir,'.gitignore'),'*\n');
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'));
  const browser = await chromium.launch({channel:'chrome',headless:true,timeout:15000,args:['--disable-gpu']});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'load',timeout:20000});
  assert.equal(await page.locator('article[data-asset]').count(),manifest.assets.length);
  assert.equal(await page.locator('#hull option').count(),Object.keys(manifest.hull_colors).length);
  assert.equal(await page.locator('#detail option').count(),Object.keys(manifest.detail_colors).length);
  assert.equal(await page.locator('article[data-asset^="carrier"]').count(),0);
  let checked=0;
  for(const pair of manifest.mix_and_match.combinations){
    await page.selectOption('#hull',pair.hull);
    await page.selectOption('#detail',pair.detail);
    const sources=await page.locator('article img').evaluateAll(images=>images.map(image=>image.getAttribute('src')));
    assert(sources.every(source=>source.endsWith('/'+pair.id+'.png')));
    checked++;
  }
  await page.selectOption('#preset','original');
  assert.equal(await page.inputValue('#hull'),'ivory');
  assert.equal(await page.inputValue('#detail'),'oxide');
  await page.check('#source');
  assert((await page.locator('article img').first().getAttribute('src')).endsWith('source_overview.png'));
  await page.click('#hull-next');
  assert.equal(await page.isChecked('#source'),false);
  assert.equal(await page.inputValue('#hull'),'red');
  await page.selectOption('#preset','white_black');
  await page.locator('article img').first().evaluate(image=>image.decode());
  await page.screenshot({path:path.join(artifactDir,'fleet-colors-desktop.png')});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  await page.screenshot({path:path.join(artifactDir,'fleet-colors-mobile.png')});
  assert.deepEqual(errors,[]);
  const report={passed:true,independent_pairs_checked:checked,asset_cards:manifest.assets.length,carrier_cards:0,original_preset_checked:true,
    source_toggle_checked:true,scroll_buttons_checked:true,mobile_no_overflow:true,page_errors:errors};
  fs.writeFileSync(path.join(root,'browser_validation.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(error=>{console.error(error);process.exitCode=1;});
