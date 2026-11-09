// Lucide (ISC) SVG → PNG в цветах палитры
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const dir=path.join(__dirname,'../assets/icons');
const colors={ochre:'#D9A441',sky:'#4FA3D9',white:'#FFFFFF',navy:'#0F1B2D'};
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:256,height:256}});
for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.svg'))){
 let svg=fs.readFileSync(path.join(dir,f),'utf8').replace(/<!--.*?-->/,'').replace('width="24"','width="256"').replace('height="24"','height="256"').replace('stroke-width="2"','stroke-width="1.75"');
 for(const [n,c] of Object.entries(colors)){
  await p.setContent(`<html><body style="margin:0;background:transparent;color:${c}">${svg}</body></html>`);
  await p.screenshot({path:path.join(dir,f.replace('.svg',`_${n}.png`)),omitBackground:true,clip:{x:0,y:0,width:256,height:256}});
 }}
await b.close();})();
