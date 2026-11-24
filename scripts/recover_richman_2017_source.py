#!/usr/bin/env python3
"""Retrieve DOI-identified Richman et al. workbook, verify publisher checksum, inspect schema."""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, re, urllib.parse, urllib.request
from openpyxl import load_workbook
DOI='10.5061/dryad.tf71f'
PAPER='10.1111/1365-2745.12657'
NAME='2016_Richman_IpomopsisSecondaryRobbing.xlsx'
TITLE='facilitated exploitation of pollination mutualisms'
def get(url,limit=8_000_000):
    req=urllib.request.Request(url,headers={'User-Agent':'BALANCE-research-source-audit/1.0','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(limit+1)
        if len(raw)>limit:raise ValueError('response size cap')
        return raw,r.url
def readjson(url):return json.loads(get(url)[0])
def title_ok(s):return TITLE in str(s).lower()
def verify_bytes(raw,expected,algorithm,size):
    if algorithm not in ('md5','sha256') or not expected or not size:raise ValueError('missing source checksum/size')
    if len(raw)!=int(size) or hashlib.new(algorithm,raw).hexdigest().lower()!=expected.lower():raise ValueError('source checksum/size mismatch')
    return {'bytes':len(raw),'md5':hashlib.md5(raw).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest(),'official_checksum':algorithm+':'+expected}
def acquire(out):
    report={'dataset_doi':DOI,'article_doi':PAPER,'expected_filename':NAME,'attempts':[],'source_authenticated':False}
    options=[]
    # The historical Dryad-Zenodo mirror often carries the original DOI, or records it as a related identifier.
    for q in ['doi:"'+DOI+'"','"'+DOI+'"','title:"Facilitated exploitation of pollination mutualisms"']:
        url='https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':q,'size':20})
        try:
            z=readjson(url)
            for r in z.get('hits',{}).get('hits',[]):
                meta=r.get('metadata',{});title=meta.get('title','')
                dois=[str(r.get('doi','')),str(meta.get('doi',''))]+[str(x.get('identifier','')) for x in meta.get('related_identifiers',[])]
                if not title_ok(title) or not any(DOI in a.lower() for a in dois):continue
                for f in r.get('files',[]):
                    if f.get('key')!=NAME:continue
                    alg,_,digest=str(f.get('checksum','')).partition(':')
                    link=f.get('links',{}).get('content') or f.get('links',{}).get('self')
                    if not link or urllib.parse.urlsplit(link).hostname not in ('zenodo.org','www.zenodo.org'):continue
                    options.append({'provider':'Zenodo mirror','record':r['id'],'metadata_url':'https://zenodo.org/api/records/'+str(r['id']),'url':link,'size':f.get('size'),'algorithm':alg,'digest':digest,'title':title,'doi_identity':dois})
            report['attempts'].append({'url':url,'hits':len(z.get('hits',{}).get('hits',[]))})
        except Exception as e:report['attempts'].append({'url':url,'error':str(e)[:300]})
        if options:break
    # Dryad authority: exact dataset DOI and version-linked file metadata.
    dry='https://datadryad.org/api/v2/datasets/'+urllib.parse.quote('doi:'+DOI,safe='')
    try:
        m=readjson(dry)
        if not title_ok(m.get('title')) or DOI not in str(m.get('identifier','')).lower():raise ValueError('Dryad identity mismatch')
        href=m.get('_links',{}).get('stash:version',{}).get('href')
        if not href:raise ValueError('missing version link')
        u=urllib.parse.urljoin('https://datadryad.org',href)
        if urllib.parse.urlsplit(u).hostname!='datadryad.org':raise ValueError('untrusted version URL')
        fs=readjson(u+'/files')
        report['dryad_metadata']={'dataset':dry,'version':u,'files':fs}
        for f in fs.get('_embedded',{}).get('stash:files',[]):
            if f.get('path')!=NAME:continue
            fid=f.get('fileId') or f.get('id')
            h=f.get('_links',{}).get('self',{}).get('href')
            if not fid and h:fid=h.rstrip('/').split('/')[-1]
            if not str(fid).isdigit():continue
            alg=str(f.get('digestType','')).lower().replace('-','')
            digest=f.get('digest');size=f.get('size')
            for u2 in ['https://datadryad.org/downloads/file_stream/'+str(fid),'https://datadryad.org/api/v2/files/'+str(fid)+'/download']:
                options.append({'provider':'Dryad','record':fid,'metadata_url':u+'/files','url':u2,'algorithm':alg,'digest':digest,'size':size,'title':m['title']})
    except Exception as e:report['attempts'].append({'url':dry,'error':str(e)[:300]})
    report['candidate_files']=options
    for opt in options:
        try:
            raw,final=get(opt['url'])
            receipt=verify_bytes(raw,opt['digest'],opt['algorithm'],opt['size'])
            # Workbook opens before receipt is promoted.
            import io
            load_workbook(io.BytesIO(raw),read_only=True,data_only=True).close()
            (out/NAME).write_bytes(raw)
            report.update({'source_authenticated':True,'selected':opt,'file_receipt':receipt})
            break
        except Exception as e:report['attempts'].append({'url':opt['url'],'error':str(e)[:300]})
    (out/'SOURCE_RECEIPT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report
def inspect(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    d={}
    for s in wb:
        rows=list(s.values)
        width=max((len(r) for r in rows),default=0)
        def norm(x):return x if x is None or isinstance(x,(int,float,str,bool)) else str(x)
        d[s.title]={'max_row':len(rows),'max_col':width,
                    'first_rows':[[norm(x) for x in r] for r in rows[:(35 if 'meta' in s.title.lower() else 8)]],
                    'nonempty_rows':sum(any(x is not None for x in r) for r in rows)}
    wb.close()
    return d
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);r=acquire(a.out)
    print('RICHMAN_SOURCE_RECEIPT '+json.dumps(r,ensure_ascii=False,default=str))
    if r['source_authenticated']:
        d=inspect(a.out/NAME)
        (a.out/'WORKBOOK_SCHEMA.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
        print('RICHMAN_SCHEMA '+json.dumps(d,ensure_ascii=False))
    else:print('RICHMAN_SOURCE_HOLD: source bytes unavailable; no biological result')
if __name__=='__main__':main()
