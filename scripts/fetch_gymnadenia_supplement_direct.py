#!/usr/bin/env python3
from __future__ import annotations
import io, json, re, sys, urllib.request
from pathlib import Path

URL='https://doi.org/10.1890/14-0119.1.sm'
UA={'User-Agent':'balance-q1b-supplement-fetcher/1'}

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.geturl(), r.headers.get_content_type(), r.read()

def main(out):
    final_url, ctype, blob = fetch(URL)
    result={'source_url':URL,'final_url':final_url,'content_type':ctype,'bytes':len(blob)}
    text=''
    if 'pdf' in ctype or blob[:4]==b'%PDF':
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(blob))
        text='\n'.join((p.extract_text() or '') for p in reader.pages)
        result['pages']=len(reader.pages)
    else:
        text=blob.decode('utf-8','replace')
    result['contains_table_a2']='Table A2' in text
    # retain compact auditable excerpts around Table A2 / flowering start only
    excerpts=[]
    for pat in ['Table A2','flowering start','Flowering start']:
        for m in re.finditer(re.escape(pat),text,re.I):
            s=max(0,m.start()-1200); e=min(len(text),m.end()+2600)
            excerpts.append(text[s:e])
            if len(excerpts)>=8: break
        if len(excerpts)>=8: break
    result['excerpts']=excerpts
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'final_url':final_url,'content_type':ctype,'bytes':len(blob),'contains_table_a2':result['contains_table_a2']}))
    if not result['contains_table_a2']:
        raise RuntimeError('supplement resolved but Table A2 text was not recovered')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: fetch_gymnadenia_supplement_direct.py OUT.json')
    main(sys.argv[1])
