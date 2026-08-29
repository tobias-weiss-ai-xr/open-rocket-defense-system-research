#!/usr/bin/env python3
"""WCAG AAA contrast audit v6 — full alpha compositing + gradient sampling in JS."""
import sys, re
from playwright.sync_api import sync_playwright

CHROME = "/home/weissto_local/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"  # override as needed

AUDIT = r"""
() => {
  const results = [];
  const all = document.querySelectorAll('body *');

  function parseColor(c){
    if(!c) return null;
    c=c.trim();
    if(c.startsWith('#')){
      c=c.slice(1);
      if(c.length===3)c=c.split('').map(x=>x+x).join('');
      const v=[parseInt(c.slice(0,2),16),parseInt(c.slice(2,4),16),parseInt(c.slice(4,6),16),1];
      return isNaN(v[0])?null:v;
    }
    const m=/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\s*\)/.exec(c);
    if(m)return [+m[1],+m[2],+m[3],m[4]?+m[4]:1];
    return null;
  }
  function lin(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);}
  function lum(p){return 0.2126*lin(p[0])+0.7152*lin(p[1])+0.0722*lin(p[2]);}
  function contrast(fg,bg){const l1=lum(fg),l2=lum(bg);const hi=Math.max(l1,l2),lo=Math.min(l1,l2);return (hi+0.05)/(lo+0.05);}
  function blend(fg,bg){const a=fg[3];return [fg[0]*a+bg[0]*(1-a),fg[1]*a+bg[1]*(1-a),fg[2]*a+bg[2]*(1-a),1];}

  function sampleGradCss(css,t){
    const inner=css.slice(css.indexOf('(')+1, css.lastIndexOf(')'));
    // split on commas at depth 0
    const parts=[]; let depth=0, cur='';
    for(const ch of inner){
      if(ch==='(')depth++;
      else if(ch===')')depth--;
      if(ch===','&&depth===0){parts.push(cur.trim());cur='';}
      else cur+=ch;
    }
    parts.push(cur.trim());
    const stops=[];
    for(const p of parts){
      if(/deg|turn|rad|^to\s/.test(p))continue;
      const m=/^\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))\s*(.*)$/.exec(p);
      if(!m)continue;
      const col=parseColor(m.group? undefined : m[1]);
      let pos=null;
      const pm=/[\d.]+%/.exec(m[2]);
      if(pm)pos=+pm[0].replace('%','')/100;
      if(col){stops.push({pos,col});}
    }
    if(stops.length===0)return null;
    // fill implicit positions
    stops.forEach((s,i)=>{ if(s.pos===null){ s.pos = i===stops.length-1?1:(i===0?0:i); } });
    if(t<=stops[0].pos)return blend(stops[0].col,[255,255,255,1]);
    if(t>=stops[stops.length-1].pos)return blend(stops[stops.length-1].col,[255,255,255,1]);
    for(let i=0;i<stops.length-1;i++){
      if(stops[i].pos<=t&&t<=stops[i+1].pos){
        const span=stops[i+1].pos-stops[i].pos||1;
        const k=(t-stops[i].pos)/span;
        const c0=stops[i].col,c1=stops[i+1].col;
        const c=[c0[0]*(1-k)+c1[0]*k,c0[1]*(1-k)+c1[1]*k,c0[2]*(1-k)+c1[2]*k,1];
        return c;
      }
    }
    return blend(stops[stops.length-1].col,[255,255,255,1]);
  }

  // backdrop compositing walk
  function resolveBackdrop(el){
    let acc=null; // accumulated; bg always treated as opaque once found
    let gInfo=null;
    let node=el;
    while(node && node!==document.documentElement){
      const cs=getComputedStyle(node);
      const bgi=cs.backgroundImage;
      if(bgi && /linear-gradient/.test(bgi)){
        // sample gradient behind accumulated acc
        const g=sampleGradCss(bgi,0.5);
        if(g){ acc = acc? blend([g[0],g[1],g[2],0.99],acc) : g; }
        return {type:'gradient', color:acc||[255,255,255,1], css:bgi};
      }
      const b=parseColor(cs.backgroundColor);
      if(b && b[3]>0.0){
        if(!acc)acc=[b[0],b[1],b[2],1];
        else acc=blend(b,acc);
        if(b[3]>=0.99) return {type:'solid', color:acc, css:null};
      }
      node=node.parentElement;
    }
    return {type: acc?'solid':'default', color: acc||[255,255,255,1], css:null};
  }

  for(const el of all){
    const directText=Array.from(el.childNodes).filter(n=>n.nodeType===3 && n.textContent.trim().length>0);
    if(directText.length===0)continue;
    const text=directText[0].textContent.trim().slice(0,50);
    if(!text)continue;
    const cs=getComputedStyle(el);
    const fg=parseColor(cs.color);
    if(!fg)continue;
    const size=parseFloat(cs.fontSize);
    const bold=parseInt(cs.fontWeight)>=700;
    const large=size>=24 || (size>=18.66&&bold);
    const need=large?4.5:7.0;
    const bd=resolveBackdrop(el);
    const bg=bd.color;
    const effFg=fg[3]<0.999?blend(fg,bg):[fg[0],fg[1],fg[2],1];
    const ratio=contrast(effFg,bg);
    if(ratio<need){
      results.push({
        cls:(typeof el.className==='string'&&el.className)?el.className:el.tagName,
        text, fg:cs.color, fgArr:effFg,
        bgType:bd.type, bgArr:bg, bgCss:bd.css?bd.css.slice(0,70):null,
        size:Math.round(size*10)/10, bold, large, ratio:Math.round(ratio*100)/100, need
      });
    }
  }
  return results;
}
"""

def main():
    urls = sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, headless=True)
        for url in urls:
            page = b.new_page(viewport={"width":1280,"height":900})
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(3000)
            res = page.evaluate(AUDIT)
            page.close()
            print(f"=== {url} : {len(res)} low-contrast text nodes ===")
            seen=set()
            for r in res:
                k=(r['cls'],r['text'])
                if k in seen: continue
                seen.add(k)
                bgdesc = f"grad[{r['bgCss']}]" if r['bgType']=='gradient' else f"solid#{''.join(f'{max(0,min(255,round(x))):02x}' for x in r['bgArr'][:3])}"
                bar = '#'*int(r['ratio']*4)
                print(f"  .{r['cls']:<34} \"{r['text']}\" ratio {r['ratio']:.2f} < {r['need']} [{'large' if r['large'] else 'normal'} {r['size']}px{' bold' if r['bold'] else ''}] bg={bgdesc}")
            if not res:
                print("  CLEAN")
        b.close()

if __name__ == '__main__':
    main()
