#!/usr/bin/env python3
"""Heiling 2018 original source discovery: exact pinned Dryad file, public mirror only."""
from __future__ import annotations
import concurrent.futures as cf
import hashlib, io, json, pathlib, urllib.parse, urllib.request
from openpyxl import load_workbook

DOI='10.5061/dryad.bh6hs70'
PAPER='10.1111/oik.05440'
NAME='Heiling.et.al.Oikos.2018.data.xlsx'
MD5='31e7e67fa98c5ffb7b4b133686191b90'
TITLE='why are some plant'
def get(url,limit=8000000,timeout=45):
    req=urllib.request.Request(url,headers={'User-Agent':'BALANCE-original-data-research/1.0','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        raw=r.read(limit+1)
        if len(raw)>limit:raise ValueError('response too large')
        return raw,r.url
def metadata(url):
    try:return {'url':url,'data':json.loads(get(url,timeout=45)[0])}
    except Exception as e:return {'url':url,'error':str(e)[:400]}
def mirror_candidates(d):
    out=[]
    for rec in d.get('hits',{}).get('hits',[]):
        m=rec.get('metadata',{})
        ids=[str(rec.get('doi','')),str(m.get('doi',''))]+[str(x.get('identifier','')) for x in m.get('related_identifiers',[])]
        if TITLE not in str(m.get('title','')).lower() or not any(DOI in x.lower() for x in ids):continue
        for f in rec.get('files',[]):
            if f.get('key')!=NAME or f.get('checksum','').lower()!='md5:'+MD5:continue
            rid=int(rec['id']);name=urllib.parse.quote(NAME)
            urls=['https://zenodo.org/api/records/'+str(rid)+'/files/'+name+'/content',
                  'https://zenodo.org/records/'+str(rid)+'/files/'+name+'?download=1',
                  'https://zenodo.org/record/'+str(rid)+'/files/'+name+'?download=1']
            out.extend({'url':u,'size':int(f['size']),'record':rid,'official_md5':MD5,'doi_identity':ids} for u in urls)
    return out
def fetch(opt):
    try:
        raw,final=get(opt['url'],timeout=70)
        if len(raw)!=opt['size'] or hashlib.md5(raw).hexdigest()!=MD5:raise ValueError('pinned file checksum/size mismatch')
        w=load_workbook(io.BytesIO(raw),data_only=True,read_only=True);w.close()
        return {**opt,'final_url':final,'authenticated':True,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},raw
    except Exception as e:return {**opt,'authenticated':False,'error':str(e)[:400]},None
def main():
    out=pathlib.Path('artifacts/heiling_source');out.mkdir(parents=True,exist_ok=False)
    queries=['doi:"'+DOI+'"','"'+DOI+'"','title:"Why are some plant" AND title:"commensalisms"']
    urls=['https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':q,'size':30}) for q in queries]
    dry='https://datadryad.org/api/v2/versions/9716/files'
    with cf.ThreadPoolExecutor(max_workers=4) as ex: rs=list(ex.map(metadata,urls+[dry]))
    options=[];logs=[]
    for r in rs:
        if 'error'in r:logs.append(r);continue
        d=r['data']
        if r['url']==dry:
            files=d.get('_embedded',{}).get('stash:files',[])
            logs.append({'url':dry,'files':files})
            for f in files:
                fid=f.get('fileId') or f.get('id') or f.get('_links',{}).get('self',{}).get('href','').split('/')[-1]
                if str(fid)!='41496' or f.get('path')!=NAME or str(f.get('digest','')).lower()!=MD5:continue
                options.extend({'url':u,'size':int(f['size']),'file_id':41496,'official_md5':MD5} for u in ['https://datadryad.org/downloads/file_stream/41496','https://datadryad.org/api/v2/files/41496/download'])
        else:
            candidates=mirror_candidates(d);options.extend(candidates)
            logs.append({'url':r['url'],'hits':len(d.get('hits',{}).get('hits',[])),'candidates':candidates})
    options=list({x['url']:x for x in options}.values())
    with cf.ThreadPoolExecutor(max_workers=6) as ex: results=list(ex.map(fetch,options))
    receipt={'dataset_doi':DOI,'paper_doi':PAPER,'pinned_md5':MD5,'metadata_attempts':logs,'download_attempts':[a for a,b in results],'source_authenticated':False}
    valid=[(a,b) for a,b in results if b is not None]
    if valid:
        a,raw=valid[0];(out/NAME).write_bytes(raw);receipt.update({'source_authenticated':True,'selected':a})
        w=load_workbook(io.BytesIO(raw),data_only=True,read_only=True)
        schema={}
        for sheet in w:
            rows=list(sheet.values)
            def norm(x):return x if x is None or isinstance(x,(str,int,float,bool)) else str(x)
            schema[sheet.title]={'rows':len(rows),'nonempty':sum(any(x is not None for x in r) for r in rows),
               'first_rows':[[norm(x) for x in r] for r in rows[:(80 if 'meta' in sheet.title.lower() else 8)]]}
        w.close();(out/'SCHEMA.json').write_text(json.dumps(schema,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
        print('HEILING_SOURCE_SCHEMA '+json.dumps(schema,ensure_ascii=False,allow_nan=False))
    (out/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    print('HEILING_SOURCE_RECEIPT '+json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
