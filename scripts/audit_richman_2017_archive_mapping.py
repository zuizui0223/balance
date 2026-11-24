#!/usr/bin/env python3
"""Audit the four focal archived effects against published rounded contrasts; not raw Richman refit."""
from __future__ import annotations
import argparse, json, math, sys, pathlib, io, zipfile, hashlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.audit_larceny_meta_stage_pairability import source_rows
def acquire(out):
    u='https://figshare.com/ndownloader/files/50193012?private_link=99df84fe5c473dc85d85'
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'BALANCE-source-audit/1.0'}),timeout=40) as r: raw=r.read(4000001)
    if len(raw)!=1572161 or hashlib.sha256(raw).hexdigest()!='84d310948e1da97c091ca27e9dcc45521cf72512ba14e30d3cd269d46e5b274c':raise ValueError('source ZIP identity')
    with zipfile.ZipFile(io.BytesIO(raw)) as z: data=z.read('update metadata/Dataset for floral larceny effect size calculation.xlsx')
    p=out/'zhong_source.xlsx';p.write_bytes(data);return p
def ratio(a,b):return (a[0]/b[1],a[1]/b[0])
def rr_bounds():
    # Assume percentage rounding to the printed precision; report as sensitivity only.
    p_ps_p=(.765,.775);p_ps_c=(.715,.725)
    fruit={'PS':(.2155,.2165),'P':(.345,.355),'C':(.5345,.5355)}
    return {'pollen deposition':{'PS/P':p_ps_p,'PS/C':p_ps_c,'P/C':ratio(p_ps_c,p_ps_p)},
            'fruit set':{t+'/'+c:ratio(fruit[t],fruit[c]) for t,c in [('PS','P'),('PS','C'),('P','C')]}}
def audit(rows):
    focal=[r for r in rows if r['ID'] in (230,231,232,233)]
    if len(focal)!=4 or any(r['ref-ID']!=55 or r['species']!='Ipomopsis_aggregata' for r in focal):raise ValueError('archive identity mismatch')
    expected=rr_bounds();results=[]
    for r in focal:
        endpoint=r['sub_response_variable']; rr=math.exp(r['yi'])
        matches=[k for k,(lo,hi) in expected[endpoint].items() if lo<=rr<=hi]
        results.append({'row':r,'response_ratio':rr,'compatible_with_printed_rounding_only':matches,'treatment_verified':False,'same_plant_covariance_known':False})
    deltas={}
    for k in ('PS/P','PS/C','P/C'):
        p=expected['pollen deposition'][k];f=expected['fruit set'][k]
        deltas[k]=[math.log(f[0]/p[1]),math.log(f[1]/p[0])]
    return {'scope':'Archive point compatibility with rounded original text; model vs raw means may differ. Bounds are rounding sensitivity, not sampling CI; no treatment mapping claimed by numeric resemblance.',
            'rows':results,'expected_ratio_intervals':expected,'published_fruit_minus_pollen_rounding_intervals':deltas}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    d=audit(source_rows(acquire(a.out)));(a.out/'RICHMAN_ZHONG_MAPPING.json').write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('RICHMAN_ARCHIVE_MAP '+json.dumps(d,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()
