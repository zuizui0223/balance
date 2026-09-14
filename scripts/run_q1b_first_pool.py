#!/usr/bin/env python3
from __future__ import annotations
import json, math, random, sys, urllib.request
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import numpy as np

# Import the frozen Impatiens reanalysis contract and reuse its parsing/model code.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_impatiens_q1b_reanalysis as imp

ROOT = Path(__file__).resolve().parents[1]
FRAGARIA = ROOT / 'data' / 'BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json'
GYMNADENIA = ROOT / 'data' / 'BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json'
T975_DF2 = 4.302652729911275


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


def _fraction_to_float(value: F, name: str) -> float:
    try:
        out = float(value)
    except OverflowError as exc:
        raise ValueError(f'{name} is finite mathematically but not representable as float') from exc
    if not math.isfinite(out):
        raise ValueError(f'{name} is finite mathematically but not representable as float')
    if value != 0 and out == 0.0:
        raise ValueError(f'{name} underflows float precision')
    return out


def _fraction_decimal(value: F) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _decimal_to_float(value: Decimal, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f'{name} is finite mathematically but not representable as float')
    if value != 0 and out == 0.0:
        raise ValueError(f'{name} underflows float precision')
    return out


def dl_mkh(yi, vi):
    """Frozen first-pool DL + modified-KH calculation for exactly k=3.

    The manuscript contract fixes the first allowed pool at three independent
    positive clusters, hence df=2 and ``T975_DF2``.  This helper therefore
    refuses other k rather than silently reusing a df=2 critical value.

    All inverse-variance algebra is exact at the supplied-float level.  Only
    the irrational square root and CI endpoints use high-range Decimal
    arithmetic before conversion back to the float-valued JSON surface.
    """
    try:
        y = tuple(float(value) for value in yi)
        v = tuple(float(value) for value in vi)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('Q1B pooling inputs must be finite numeric values') from exc
    if len(y) != 3 or len(v) != 3:
        raise ValueError('first Q1B pool is frozen at exactly k=3 (df=2)')
    if not all(math.isfinite(value) for value in (*y, *v)):
        raise ValueError('Q1B pooling inputs must be finite')
    if not all(value > 0.0 for value in v):
        raise ValueError('Q1B within-study variances must be strictly positive')

    yq = tuple(F.from_float(value) for value in y)
    vq = tuple(F.from_float(value) for value in v)
    weights = tuple(F(1, 1) / value for value in vq)
    sum_w = sum(weights, F(0, 1))
    mu_f_q = sum((w * estimate for w, estimate in zip(weights, yq)), F(0, 1)) / sum_w
    Q_q = sum((w * (estimate - mu_f_q) ** 2 for w, estimate in zip(weights, yq)), F(0, 1))
    df = 2
    c_q = sum_w - sum((w * w for w in weights), F(0, 1)) / sum_w
    if c_q <= 0:
        raise ValueError('Q1B inverse-variance geometry is degenerate')
    tau2_q = max(F(0, 1), (Q_q - df) / c_q)

    random_weights = tuple(F(1, 1) / (variance + tau2_q) for variance in vq)
    sum_wr = sum(random_weights, F(0, 1))
    mu_q = sum((w * estimate for w, estimate in zip(random_weights, yq)), F(0, 1)) / sum_wr
    q_q = sum((w * (estimate - mu_q) ** 2 for w, estimate in zip(random_weights, yq)), F(0, 1)) / df
    se2_q = max(F(1, 1), q_q) / sum_wr
    i2_q = max(F(0, 1), (Q_q - df) / Q_q) * 100 if Q_q > 0 else F(0, 1)

    mu_f = _fraction_to_float(mu_f_q, 'fixed-effect mean')
    Q = _fraction_to_float(Q_q, 'Cochran Q')
    tau2 = _fraction_to_float(tau2_q, 'DerSimonian-Laird tau^2')
    mu = _fraction_to_float(mu_q, 'random-effects mean')
    I2 = _fraction_to_float(i2_q, 'I^2')

    with localcontext() as ctx:
        ctx.prec = 80
        se_decimal = _fraction_decimal(se2_q).sqrt()
        mu_decimal = _fraction_decimal(mu_q)
        t_decimal = Decimal.from_float(T975_DF2)
        lo_decimal = mu_decimal - t_decimal * se_decimal
        hi_decimal = mu_decimal + t_decimal * se_decimal
    se = _decimal_to_float(se_decimal, 'modified Knapp-Hartung standard error')
    ci = [
        _decimal_to_float(lo_decimal, 'modified Knapp-Hartung lower CI'),
        _decimal_to_float(hi_decimal, 'modified Knapp-Hartung upper CI'),
    ]
    return {'k':3,'mu_random':mu,'se_mkh':se,'ci95_mkh':ci,'tau2_DL':tau2,'Q_fixed':Q,'I2_percent':I2,'mu_fixed':mu_f}


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
