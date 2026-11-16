#!/usr/bin/env python3
"""Post-open 2026 Desfontainia two-part seed audit (descriptive, noncausal).

Reads one original 40-shrub worksheet through the previously MD5-gated reader.
Provides two-part arithmetic and paired precision limits, not a structural
architecture fitness, nectar mediation, or randomized robbery effect.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_desfontainia_fitness_gate import (  # noqa: E402
    ORIGINAL_MD5, source_sheet, summarize_seed,
)

T39_90_TWO_SIDED = 1.684875121711225  # t.ppf(.95, df=39); fixed n=40
BOOTSTRAP_DRAWS=20000
BOOTSTRAP_SEED=20261116


def exact_two_sided_binomial(k:int,n:int) -> float:
    """Exact two-sided sign reference for p=1/2; returns 1 for n=0."""
    if n<0 or k<0 or k>n:raise ValueError('Invalid binomial count')
    if n==0:return 1.0
    tail=min(k,n-k)
    return min(1.0,2*sum(math.comb(n,j) for j in range(tail+1))/(2**n))


def _component_stats(rows):
    y0=[float(r[2]) for r in rows]
    y1=[float(r[3]) for r in rows]
    n=len(rows)
    p0=sum(v>0 for v in y0)/n
    p1=sum(v>0 for v in y1)/n
    pos0=sum(y0)/sum(v>0 for v in y0) if any(v>0 for v in y0) else 0.0
    pos1=sum(y1)/sum(v>0 for v in y1) if any(v>0 for v in y1) else 0.0
    prev=(p1-p0)*pos0
    intensity=p1*(pos1-pos0)
    delta=statistics.mean(y1)-statistics.mean(y0)
    if not math.isclose(prev+intensity,delta,rel_tol=0,abs_tol=1e-9):
        raise AssertionError('Two-part arithmetic decomposition failed')
    return p0,p1,pos0,pos1,prev,intensity,delta


def _paired_bootstrap(rows):
    """Preserves shrub pairs; conditional means are descriptive selected outcomes."""
    rng=random.Random(BOOTSTRAP_SEED)
    out={k:[] for k in ('mean_delta','presence_delta','conditional_positive_mean_delta',
                         'prevalence_component','positive_magnitude_component')}
    for _ in range(BOOTSTRAP_DRAWS):
        sample=[rows[rng.randrange(40)] for j in range(40)]
        p0,p1,mu0,mu1,prev,mag,delta=_component_stats(sample)
        out['mean_delta'].append(delta)
        out['presence_delta'].append(p1-p0)
        out['conditional_positive_mean_delta'].append(mu1-mu0)
        out['prevalence_component'].append(prev)
        out['positive_magnitude_component'].append(mag)
    return {key:[sorted(vals)[int(.025*BOOTSTRAP_DRAWS)],
                 sorted(vals)[int(.975*BOOTSTRAP_DRAWS)-1]] for key,vals in out.items()}


def summarize_two_part(rows:list[list[float]]) -> dict[str,Any]:
    original=summarize_seed(rows)  # immutable source group/member/seed non-negativity checks
    p0,p1,mu0,mu1,prev,mag,delta=_component_stats(rows)
    d=[float(r[3])-float(r[2]) for r in rows]
    mean_diff=statistics.mean(d)
    se=statistics.stdev(d)/math.sqrt(len(d))
    ci90=[mean_diff-T39_90_TWO_SIDED*se, mean_diff+T39_90_TWO_SIDED*se]
    ci95=original['paired_seed_difference_plusR_minusR']['t_95_interval']
    base=original['mean_seeds_by_treatment']['plusP_minusR']
    if base<=0:raise ValueError('Positive protected mean needed for relative margin scenarios')
    thresholds={}
    for pct in (10,20,50):
        margin=base*pct/100
        thresholds[f'relative_{pct}_percent']={
             'illustrative_half_width_seeds':margin,
             '90ci_within_bounds':bool(ci90[0]>-margin and ci90[1]<margin)}
    sign_positive=sum(v>0 for v in d)
    sign_negative=sum(v<0 for v in d)
    exclusive0=sum((r[2]>0) and (r[3]==0) for r in rows)
    exclusive1=sum((r[2]==0) and (r[3]>0) for r in rows)
    leave_one=[(sum(d)-d[i])/39 for i in range(40)]
    return {
        'schema':'BALANCE_DESFONTAINIA_TWO_PART_PRECISION_V1',
        'n_shrubs':40,
        'grain':'one distinct outcome flower per treatment, paired by shrub; treatments not randomly comparable',
        'source_doi':'10.5281/zenodo.18895003','source_md5':ORIGINAL_MD5,
        'seed_presence':{'protected':sum(r[2]>0 for r in rows),
                         'naturally_pierced':sum(r[3]>0 for r in rows)},
        'positive_only_means':{'protected':mu0,'naturally_pierced':mu1},
        'overall_means':{'protected':statistics.mean(float(r[2]) for r in rows),
                         'naturally_pierced':statistics.mean(float(r[3]) for r in rows)},
        'arithmetic_decomposition':{
            'reference_order':'first protected success-conditional mean for change in success prevalence; then naturally pierced prevalence for positive-magnitude difference',
            'prevalence_component':prev,
            'positive_magnitude_component':mag,
            'reconstructed_mean_difference':prev+mag,
            'components_are_causal_or_unique':False,
        },
        'paired_presence':{
            'difference':p1-p0,
            'protected_positive_pierced_zero':exclusive0,
            'protected_zero_pierced_positive':exclusive1,
            'exact_discordance_two_sided_reference_p':exact_two_sided_binomial(exclusive0,exclusive0+exclusive1),
        },
        'paired_difference':{
            'mean':mean_diff,'median':statistics.median(d),
            'n_positive':sign_positive,'n_negative':sign_negative,
            'n_equal':sum(v==0 for v in d),
            'exact_sign_two_sided_reference_p':exact_two_sided_binomial(sign_positive,sign_positive+sign_negative),
            '95ci_bounds':ci95,
            'leave_one_shrub_out_mean_min_max':[min(leave_one),max(leave_one)],
        },
        'equivalence_sensitivity':{
            'post_open_exploratory_margins_not_preregistered':True,
            '90ci_bounds':ci90,
            **thresholds,
            'minimum_symmetric_half_width_for_90ci':max(abs(ci90[0]),abs(ci90[1])),
            'minimum_symmetric_half_width_as_percent_protected_mean':100*max(abs(ci90[0]),abs(ci90[1]))/base,
            'margins_test_only_observed_comparison_not_randomized_causal_robbery_effect':True,
        },
        'paired_shrub_bootstrap95':_paired_bootstrap(rows),
        'interpretation_guardrails':{
            'absence_of_seed_cost_proven':False,
            'causal_robbery_effect_identified':False,
            'conditional_positive_mean_causal':False,
            'nectar_to_seed_same_flower_mediation_identified':False,
            'structural_BALANCE_worldline_measured':False,
            'independent_biological_studies_added':0,
            'original_V4_coder_or_outcome_changed':False,
        },
    }


def audit(path:Path):
    return summarize_two_part(source_sheet(path,6,['Plant','Seed (-P-R)','Seeds (+P-R)','Seeds (+P+R)']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.source)
    if args.out.exists():raise FileExistsError('Refuse overwrite of source receipt')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paired_shrub_bootstrap95'},ensure_ascii=False))

if __name__=='__main__':main()
