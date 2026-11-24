#!/usr/bin/env python3
"""Recover exact registered public mirror; accept only the pinned Dryad bytes."""
import concurrent.futures, hashlib, io, json, pathlib, urllib.request
from openpyxl import load_workbook
NAME='2016_Richman_IpomopsisSecondaryRobbing.xlsx'
MD5='7bd93c8f75bfff9861263d304eaba799'
SIZE=67814
URLS=['https://zenodo.org/api/records/4975584/files/'+NAME+'/content',
      'https://zenodo.org/records/4975584/files/'+NAME+'?download=1',
      'https://zenodo.org/record/4975584/files/'+NAME+'?download=1']
def fetch(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'BALANCE-research-source-audit/1.0'})
        with urllib.request.urlopen(req,timeout=70) as f: raw=f.read(SIZE+1); final=f.url
        if len(raw)!=SIZE or hashlib.md5(raw).hexdigest()!=MD5:raise ValueError('pinned original mismatch')
        w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True);w.close()
        return {'url':url,'final_url':final,'source_authenticated':True,'bytes':len(raw),'md5':MD5,'sha256':hashlib.sha256(raw).hexdigest()},raw
    except Exception as e:return {'url':url,'source_authenticated':False,'error':str(e)[:500]},None
def main():
    out=pathlib.Path('artifacts/richman_direct_mirror');out.mkdir(parents=True,exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: result=list(ex.map(fetch,URLS))
    receipt={'doi':'10.5061/dryad.tf71f','record':4975584,'attempts':[a for a,b in result],'source_authenticated':False}
    valid=[(a,b) for a,b in result if b is not None]
    if valid:
        a,raw=valid[0];(out/NAME).write_bytes(raw);receipt.update({'source_authenticated':True,'selected':a})
        from scripts.recover_richman_2017_source import inspect
        schema=inspect(out/NAME);(out/'WORKBOOK_SCHEMA.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n')
        print('RICHMAN_DIRECT_SCHEMA '+json.dumps(schema,ensure_ascii=False))
    (out/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('RICHMAN_DIRECT_RECEIPT '+json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
