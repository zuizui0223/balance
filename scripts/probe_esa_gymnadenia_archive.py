#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, mimetypes, sys, urllib.request
from pathlib import Path

BASE='https://esapubs.org/archive/ecol/E096/022/'
CANDIDATES=[
    '',
    'appendix-A.php',
    'appendix-A.htm',
    'appendix-A.html',
    'E096-022-A1.pdf',
    'E096-022-A1.doc',
    'E096-022-A1.docx',
    'E096-022-A1.xls',
    'E096-022-A1.xlsx',
]
UA={'User-Agent':'balance-q1b-esa-probe/1'}

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    try:
        with urllib.request.urlopen(req,timeout=60) as fh:
            b=fh.read()
            return {'ok':True,'status':getattr(fh,'status',200),'url':fh.geturl(),'content_type':fh.headers.get('Content-Type',''),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'body':b}
    except Exception as e:
        return {'ok':False,'error':repr(e),'url':url}

def main(outdir):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name in CANDIDATES:
        r=fetch(BASE+name)
        row={k:v for k,v in r.items() if k!='body'}
        row['candidate']=name or 'INDEX'
        manifest.append(row)
        if r.get('ok') and r.get('body'):
            suffix=Path(name).suffix if name else '.html'
            if not suffix: suffix='.bin'
            fn=('index' if not name else name.replace('/','_'))
            p=out/fn
            p.write_bytes(r['body'])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
    if not any(x.get('ok') for x in manifest):
        raise SystemExit('no ESA endpoint succeeded')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: probe_esa_gymnadenia_archive.py OUTDIR')
    main(sys.argv[1])
