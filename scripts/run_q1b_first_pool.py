#!/usr/bin/env python3
from __future__ import annotations
import json, random, sys, urllib.request
from pathlib import Path
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT))

# Import the frozen Impatiens reanalysis contract and the pure pooling algebra.
import run_impatiens_q1b_reanalysis as imp
from balance_domain.q1b_pooling import dl_mkh

FRAGARIA = ROOT / 'data' / 'BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json'
GYMNADENIA = ROOT / 'data' / 'BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json'


def impatiens_cluster_receipt():
    req = urllib.request.Request(imp.ARCHIVE_URL, headers={'User-Agent':'balance-q1b-first-pool/1'})
    with urllib.request.urlopen(req, timeout=90) as fh:
        text = imp.find_processed_csv(fh.read())
    rows = imp.parse_rows(text)
    means, sds = {}, {}
    for k in (*imp.TRAITS, imp.PHENOLOGY):
        a=np.array([r[k] for r in rows],float)
        means[k]=float(a.mean()); sds[k]=float(a.std(ddof=1))
    cells={k:[r for r in rows if (r['Pollination'],r['Florivory'])==k] for k in imp.TREATMENT_ORDER}
    observed=imp.slopes_for_sample(cells,means,sds)
    theta_obs=[]
    for t in imp.TRAITS:
        theta_obs.append(imp.C @ np.array(observed[t],float))
    theta_obs=np.vstack(theta_obs)
    cluster_obs=theta_obs.mean(axis=0)
    rng=random.Random(imp.SEED)
    cluster_boot=[]
    for _ in range(imp.BOOTSTRAPS):
        s=imp.slopes_for_sample(cells,means,sds,rng)
        th=np.vstack([imp.C @ np.array(s[t],float) for t in imp.TRAITS])
        cluster_boot.append(th.mean(axis=0))
    B=np.asarray(cluster_boot,float)
    cov=np.cov(B,rowvar=False,ddof=1)
    se=np.sqrt(np.diag(cov))
    ci=np.quantile(B,[0.025,0.975],axis=0)
    return {
      'source':'Soper_Gorden_Adler_2018',
      'study_doi':imp.STUDY_DOI,
      'aggregation_rule':'equal_weight_mean_across_all_predeclared_traits',
      'traits':list(imp.TRAITS),
      'contrast_order':list(imp.CONTRAST_NAMES),
      'mediated_contrasts':cluster_obs.tolist(),
      'contrast_standard_errors':se.tolist(),
      'contrast_covariance':cov.tolist(),
      'bootstrap_replicates':imp.BOOTSTRAPS,
      'bootstrap_seed':imp.SEED,
      'ci95_bootstrap':ci.T.tolist(),
      'effect_size_status':'EFFECT_SIZE_READY_CLUSTER_AGGREGATE',
      'claim_ceiling':'equal-weight cluster summary of preregistered Q1B traits; not direct BALANCE occupancy'
    }


def main(outdir):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    frag=json.loads(FRAGARIA.read_text())
    gym=json.loads(GYMNADENIA.read_text())
    impc=impatiens_cluster_receipt()
    (out/'BALANCE_IMPATIENS_Q1B_CLUSTER_AGGREGATE_V1.json').write_text(json.dumps(impc,indent=2),encoding='utf-8')
    studies=[
      {'study':'Fragaria','theta':frag['mediated_contrasts'],'cov':frag['contrast_covariance']},
      {'study':'Impatiens','theta':impc['mediated_contrasts'],'cov':impc['contrast_covariance']},
      {'study':'Gymnadenia','theta':gym['mediated_contrasts'],'cov':gym['contrast_covariance']},
    ]
    names=frag['contrast_order']
    pooled={}
    for j,name in enumerate(names):
        yi=[s['theta'][j] for s in studies]
        vi=[s['cov'][j][j] for s in studies]
        pooled[name]={**dl_mkh(yi,vi),'study_effects':[{'study':s['study'],'estimate':yi[i],'variance':vi[i]} for i,s in enumerate(studies)]}
    report={
      'analysis':'BALANCE_Q1B_FIRST_ALLOWED_POOL_V1',
      'pool_gate':'OPEN_3_OF_3_EFFECT_SIZE_READY_POSITIVE_CLUSTERS',
      'independent_clusters':3,
      'cluster_names':[s['study'] for s in studies],
      'method':'componentwise DerSimonian-Laird random effects with modified Knapp-Hartung t(df=2) intervals; full within-study covariance retained but not used to estimate an underidentified 4x4 between-study covariance with k=3',
      'contrast_order':names,
      'pooled':pooled,
      'claim_ceiling':'pooled Q1B mediated-selection contrasts only; does not identify direct BALANCE occupancy, W_S*, W_D*, rho, Phi, xi, or d_B',
      'prohibited':'do not count Impatiens traits as independent clusters; do not infer full multivariate between-study covariance from k=3'
    }
    (out/'BALANCE_Q1B_FIRST_POOL_V1.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: run_q1b_first_pool.py OUTDIR')
    main(sys.argv[1])
