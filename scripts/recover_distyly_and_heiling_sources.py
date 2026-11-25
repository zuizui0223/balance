#!/usr/bin/env python3
"""Bounded public original source recovery for Tirpitzia and Corydalis."""
from __future__ import annotations
import concurrent.futures as cf, hashlib, io, json, pathlib, urllib.parse as u, urllib.request as req
from openpyxl import load_workbook
SPECS={
 'tirpitzia':{'doi':'10.5061/dryad.6hdr7sr62','title':'nectar robbing by bees affects the reproductive fitness','pinned':None},
 'heiling':{'doi':'10.5061/dryad.bh6hs70','title':'why are some plant','pinned':{'Heiling.et.al.Oikos.2018.data.xlsx':(122150,'31e7e67fa98c5ffb7b4b133686191b90')}}}
def get(url,limit=12_000_000,timeout=40):
    with req.urlopen(req.Request(url,headers={'User-Agent':'BALANCE-source-audit/1.0','Accept':'*/*'}),timeout=timeout) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError('size cap')
        return b,r.url
def meta(url):
    try:return json.loads(get(url)[0]),None
    except Exception as e:return None,str(e)[:300]
def one(name,spec,out):
    doi=spec['doi'];r={'doi':doi,'attempts':[],'source_authenticated':False,'files':[]}
    base='https://datadryad.org/api/v2/datasets/'+u.quote('doi:'+doi,safe='')
    d,e=meta(base);r['attempts'].append({'url':base,'error':e})
    files={}
    if d:
        if spec['title'] not in str(d.get('title','')).lower() or doi not in str(d.get('identifier','')).lower():raise ValueError('DOI identity mismatch')
        href=d.get('_links',{}).get('stash:version',{}).get('href')
        if href:
            url=u.urljoin('https://datadryad.org',href)+'/files'
            f,e=meta(url);r['attempts'].append({'url':url,'error':e})
            for x in (f or {}).get('_embedded',{}).get('stash:files',[]):
                k=x['path'];i=x['_links']['self']['href'].split('/')[-1]
                if not i.isdigit() or '/' in k or '\\' in k or not k.lower().endswith(('.xlsx','.xls','.csv','.zip','.txt','.md')):continue
                if x.get('digestType','').lower()!='md5':continue
                files[k]={'size':int(x['size']),'md5':x['digest'],'file_id':i,'urls':['https://datadryad.org/downloads/file_stream/'+i,'https://datadryad.org/api/v2/files/'+i+'/download']}
    if spec['pinned']:
        for k,(n,h) in spec['pinned'].items():
            if k in files and (files[k]['size'],files[k]['md5'])!=(n,h):raise ValueError('official source identity changed')
            files.setdefault(k,{'size':n,'md5':h,'urls':[]})
    queries=['doi:"'+doi+'"','title:"'+spec['title']+'"']
    urls=['https://zenodo.org/api/records?'+u.urlencode({'q':q,'size':10}) for q in queries]
    with cf.ThreadPoolExecutor(max_workers=2) as ex: metas=list(ex.map(meta,urls))
    for url,(z,e) in zip(urls,metas):
        r['attempts'].append({'url':url,'error':e,'hits':len((z or {}).get('hits',{}).get('hits',[]))})
        for hit in (z or {}).get('hits',{}).get('hits',[]):
            m=hit.get('metadata',{});ids=[str(hit.get('doi','')),str(m.get('doi',''))]+[str(x.get('identifier','')) for x in m.get('related_identifiers',[])]
            if spec['title'] not in str(m.get('title','')).lower() or not any(doi in a.lower() for a in ids):continue
            rid=int(hit['id'])
            for f in hit.get('files',[]):
                k=f.get('key')
                if k not in files:continue
                q=files[k]
                if f.get('checksum','').lower()!='md5:'+q['md5'].lower() or int(f['size'])!=q['size']:continue
                q['urls']+=['https://zenodo.org/api/records/'+str(rid)+'/files/'+u.quote(k)+'/content','https://zenodo.org/records/'+str(rid)+'/files/'+u.quote(k)+'?download=1']
                q['mirror_record']=rid
    r['official_files']=files
    def fetch(item):
        k,f,url=item
        try:
            b,final=get(url,timeout=45)
            if len(b)!=f['size'] or hashlib.md5(b).hexdigest()!=f['md5']:raise ValueError('pinned checksum mismatch')
            if k.endswith('.xlsx'):load_workbook(io.BytesIO(b),read_only=True,data_only=True).close()
            return {'name':k,'url':url,'final':final,'authenticated':True,'size':len(b),'sha256':hashlib.sha256(b).hexdigest()},b
        except Exception as e:return {'name':k,'url':url,'authenticated':False,'error':str(e)[:300]},None
    jobs=[(k,f,url) for k,f in files.items() if f['size']<=12_000_000 for url in dict.fromkeys(f['urls'])]
    with cf.ThreadPoolExecutor(max_workers=8) as ex: results=list(ex.map(fetch,jobs))
    r['downloads']=[v for v,b in results];seen=set()
    for v,b in results:
        k=v['name']
        if b is None or k in seen:continue
        seen.add(k);(out/k).write_bytes(b);r['files'].append(v)
        if k.endswith('.xlsx'):
            w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
            schema={s.title:{'rows':s.max_row,'cols':s.max_column,'first_rows':[[x if x is None or isinstance(x,(int,float,str,bool)) else str(x) for x in row] for row in s.iter_rows(max_row=min(s.max_row or 8,8),values_only=True)]} for s in w};w.close()
            (out/(k+'.schema.json')).write_text(json.dumps(schema,indent=2,ensure_ascii=False,default=str))
            print('BALANCE_ORIGINAL_SCHEMA '+json.dumps({'source':name,'file':k,'schema':schema},ensure_ascii=False,default=str))
    r['source_authenticated']=bool(seen);r['all_listed_supported_files_authenticated']=bool(files) and seen==set(files)
    (out/'RECEIPT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print('BALANCE_ORIGINAL_RECEIPT '+json.dumps({'source':name,**r},ensure_ascii=False))
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',choices=SPECS,required=True);a=p.parse_args();out=pathlib.Path('artifacts')/a.source;out.mkdir(parents=True,exist_ok=False);one(a.source,SPECS[a.source],out)
if __name__=='__main__':main()
