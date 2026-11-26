#!/usr/bin/env python3
"""Recover original Tirpitzia female-stage files with independent Dryad SHA256 and Zenodo MD5."""
import concurrent.futures as cf,hashlib,json,pathlib,urllib.request,math
import xlrd
MANIFEST=pathlib.Path('results/stage_dependence_small_n/TIRPITZIA_FEMALE_FILE_MANIFEST_20261126.json')
def get(x):
    for url in x['urls']:
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'BALANCE-original-source-audit/1.0'}),timeout=30) as r:b=r.read(x['size']+1)
            if len(b)!=x['size'] or hashlib.sha256(b).hexdigest()!=x['sha256'] or hashlib.md5(b).hexdigest()!=x['md5']:raise ValueError('two-source checksum mismatch')
            return {**x,'authenticated':True,'selected_url':url},b
        except Exception as e:err=str(e)
    return {**x,'authenticated':False,'error':err},None
def schema(b):
    w=xlrd.open_workbook(file_contents=b)
    def norm(v):return v if not isinstance(v,float) or math.isfinite(v) else str(v)
    return {s.name:{'nrows':s.nrows,'ncols':s.ncols,'first_rows':[[norm(v) for v in s.row_values(i)] for i in range(min(s.nrows,12))],
       'nonempty_rows':sum(any(v!='' for v in s.row_values(i)) for i in range(s.nrows))} for s in w.sheets()}
def main():
    manifest=json.loads(MANIFEST.read_text());assert manifest['doi']=='10.5061/dryad.6hdr7sr62'
    out=pathlib.Path('artifacts/tirpitzia_female_original');out.mkdir(parents=True,exist_ok=False)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(get,manifest['files']))
    receipts=[]
    for x,b in r:
        receipts.append(x)
        if b is None:continue
        (out/x['name']).write_bytes(b)
        if x['name'].endswith('.xls'):
            z=schema(b);(out/(x['name']+'.schema.json')).write_text(json.dumps(z,indent=2,ensure_ascii=False,allow_nan=False))
            print('TIRPITZIA_FEMALE_SCHEMA '+json.dumps({'file':x['name'],'schema':z},ensure_ascii=False,allow_nan=False))
        else:print('TIRPITZIA_README '+json.dumps(b.decode('utf-8-sig',errors='strict'),ensure_ascii=False))
    result={'doi':manifest['doi'],'files':receipts,'n_authenticated':sum(x['authenticated'] for x in receipts),'all_authenticated':all(x['authenticated'] for x in receipts)}
    (out/'RECEIPT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print('TIRPITZIA_FEMALE_RECEIPT '+json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
