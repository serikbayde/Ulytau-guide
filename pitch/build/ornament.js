// Стилизованный геометричный орнамент «қошқар мүйіз» (рисуем сами, SVG → PNG)
const {chromium}=require('playwright');const path=require('path');
const horn=(x,y,s)=>`<g transform="translate(${x},${y}) scale(${s})">
<path d="M0,40 L0,10 M0,10 C0,-12 28,-16 32,0 C35,13 20,18 15,9" />
<path d="M0,10 C0,-12 -28,-16 -32,0 C-35,13 -20,18 -15,9" />
<path d="M-10,40 L0,30 L10,40 L0,50 Z" /></g>`;
const svg=(c)=>`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 300 300">
<g fill="none" stroke="${c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
<path d="M8,292 L8,8 L292,8" stroke-width="2"/><path d="M16,292 L16,16 L292,16" stroke-width="1" opacity=".55"/>
<path d="M50,30 L70,50 L50,70 L30,50 Z" stroke-width="2.6"/><path d="M50,40 L60,50 L50,60 L40,50 Z" fill="${c}"/>
${horn(115,42,0.9)} ${horn(180,42,0.7)} ${horn(235,42,0.5)}
<g transform="rotate(-90 42 115)">${horn(42,115,0.9)}</g><g transform="rotate(-90 42 180)">${horn(42,180,0.7)}</g><g transform="rotate(-90 42 235)">${horn(42,235,0.5)}</g>
</g></svg>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:600,height:600}});
for(const [n,c] of [['ochre','#D9A441'],['sky','#4FA3D9']]){
 await p.setContent(`<html><body style="margin:0;background:transparent">${svg(c)}</body></html>`);
 await p.screenshot({path:path.join(__dirname,`../assets/ornament_${n}.png`),omitBackground:true,clip:{x:0,y:0,width:600,height:600}});}
await b.close();})();
