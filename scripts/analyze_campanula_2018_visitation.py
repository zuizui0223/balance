#!/usr/bin/env python3
"""Exploratory one-species analysis of a checksum-bound published CSV extract.

Numerical dependencies are optional; original V4 inputs are never read or edited.
Install numpy scipy statsmodels to execute. The CSV was exported from the
published MD5-verified workbook using artifact_tool; it is not individual-plant data.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/external/campanula_2018/population23.csv'
CSV_SHA256 = 'b66ec8c1471ddfe08bcfca990cb907eadcf0898f7bef45f9fdc28257a4135cde'
RATE_FIELDS = ['Bumblebee Rate', 'Megachile Rate', 'Small Rate']
FIELDS = ['Population', 'Latitude', 'Longitude'] + RATE_FIELDS + ['Pollen Limitation 2016']


def validate_population(rows):
    if len(rows) != 23 or len({r.get('Population') for r in rows}) != 23:
        raise ValueError('Require 23 distinct original populations')
    for row in rows:
        if not row.get('Population'):
            raise ValueError('Missing population identity')
        for key in FIELDS[1:]:
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise ValueError('All source fields must be numeric')
            if not math.isfinite(value):
                raise ValueError('All source fields must be finite')
        if any(row[key] < 0 for key in RATE_FIELDS + ['Pollen Limitation 2016']):
            raise ValueError('Rates and archived PL must be nonnegative')
        if sum(row[key] for key in RATE_FIELDS) <= 0:
            raise ValueError('Composition requires positive total visitation')
    return rows


def load_population(path=SOURCE):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CSV_SHA256:
        raise ValueError('Original population extract checksum changed')
    reader = csv.DictReader(raw.decode('utf-8').splitlines())
    if reader.fieldnames != FIELDS:
        raise ValueError('Source headers changed')
    rows = [{k: (v if k == 'Population' else float(v)) for k, v in row.items()} for row in reader]
    return validate_population(rows)


def fit_summary(y, predictors, names):
    import numpy as np
    import statsmodels.api as sm
    X = np.column_stack([np.ones(len(y)), predictors])
    if not np.isfinite(X).all() or not np.isfinite(y).all():
        raise ValueError('Nonfinite design')
    if np.linalg.matrix_rank(X) != X.shape[1]:
        raise ValueError('Design is rank deficient')
    fit = sm.OLS(y, X).fit()
    robust = fit.get_robustcov_results(cov_type='HC3')
    k = X.shape[1] + 1  # Include estimated residual variance in AICc.
    if len(y) <= k + 1:
        raise ValueError('Insufficient sample size for AICc')
    hat = fit.get_influence().hat_matrix_diag
    if np.any(hat >= 1 - 1e-12):
        raise ValueError('Leave-one-out design is not estimable')
    loo = np.array([sm.OLS(y[np.arange(len(y)) != j], X[np.arange(len(y)) != j]).fit().params
                    for j in range(len(y))])
    coefficients = []
    for j, name in enumerate(['intercept'] + names):
        coefficients.append({
            'name': name, 'estimate': float(fit.params[j]),
            'ci95': fit.conf_int()[j].tolist(), 'p': float(fit.pvalues[j]),
            'hc3_ci95': robust.conf_int()[j].tolist(), 'hc3_p': float(robust.pvalues[j]),
            'loo_positive': int((loo[:, j] > 0).sum()), 'loo_negative': int((loo[:, j] < 0).sum())})
    return {'n': len(y), 'parameter_count_with_variance': k,
            'r2': float(fit.rsquared), 'adj_r2': float(fit.rsquared_adj),
            'aicc': float(fit.aic + 2 + 2 * k * (k + 1) / (len(y) - k - 1)),
            'loocv_rmse': float(np.sqrt(np.mean((fit.resid / (1 - hat)) ** 2))),
            'max_leverage': float(hat.max()), 'coefficients': coefficients}


def analyze(rows):
    import numpy as np
    import statsmodels.api as sm
    validate_population(rows)
    rates = np.array([[r[k] for k in RATE_FIELDS] for r in rows], float)
    pl = np.array([r['Pollen Limitation 2016'] for r in rows], float)
    total = rates.sum(axis=1)
    geo = np.array([[r['Latitude'], r['Longitude']] for r in rows], float)
    geo -= geo.mean(axis=0)
    designs = {
        'intercept_only': (np.empty((len(rows), 0)), []),
        'total_visits': (np.log(total + .1)[:, None], ['log_total_plus_0.1']),
        'three_visitor_rates': (np.log(rates + .1), ['log_bumble_plus_0.1', 'log_megachile_plus_0.1', 'log_small_plus_0.1']),
        'total_and_composition': (np.column_stack([np.log(total + .1), rates[:, 1] / total, rates[:, 2] / total]),
                                  ['log_total_plus_0.1', 'megachile_fraction', 'small_fraction'])}
    outcomes = {}
    for outcome, y in [('sqrt_archived_PL', np.sqrt(pl)), ('archived_PL', pl)]:
        results = {name: fit_summary(y, X, names) for name, (X, names) in designs.items()}
        for name in ['total_visits', 'three_visitor_rates', 'total_and_composition']:
            X, names = designs[name]
            results[name + '_geography'] = fit_summary(y, np.column_stack([X, geo]), names + ['latitude_centered', 'longitude_centered'])
        outcomes[outcome] = results
    y = np.sqrt(pl)
    X = np.log(rates + .1)
    standardized = sm.OLS((y-y.mean())/y.std(ddof=1), sm.add_constant((X-X.mean(axis=0))/X.std(axis=0, ddof=1))).fit()
    primary = outcomes['sqrt_archived_PL']
    return {'schema': 'BALANCE_CAMPANULA_2018_EXPLORATORY_V1',
            'status': 'POST_PUBLICATION_WITHIN_SPECIES_EXPLORATORY',
            'independent_plant_species': 1, 'population_count': len(rows),
            'archived_PL_zero_count': int((pl == 0).sum()),
            'archived_PL_note': 'Negative values were already truncated upstream; article says 3, archive contains 2 zeros. Do not impute a third.',
            'source_csv_sha256': CSV_SHA256,
            'original_standardized_slopes': standardized.params[1:].tolist(),
            'composition_LOO_RMSE_relative_reduction': 1-primary['total_and_composition']['loocv_rmse']/primary['total_visits']['loocv_rmse'],
            'outcomes': outcomes, 'causal_architecture_test': False,
            'V4_inputs_modified': False, 'external_validation': False,
            'limitations': ['Selected existing species, not independent cross-species meta-analysis',
                           'Observational population visitation association, not randomized visitor exclusion',
                           'LOOCV is internal and not spatially blocked',
                           'Linear latitude/longitude are sensitivity covariates, not a full spatial model',
                           'Share coefficients are substitutions relative to bumblebee visits at fixed total and Megachile share',
                           'Native-PL geography ordinary interval includes zero; all sensitivities retained']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=SOURCE)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(load_population(args.input))
    args.out_dir.mkdir(parents=True, exist_ok=False)
    (args.out_dir/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    with (args.out_dir/'MODEL_COMPARISON.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['outcome','model','n','r2','aicc','loocv_rmse'])
        for outcome, models in result['outcomes'].items():
            for name, r in models.items():
                writer.writerow([outcome,name,r['n'],r['r2'],r['aicc'],r['loocv_rmse']])
    print(json.dumps({k:v for k,v in result.items() if k != 'outcomes'}, indent=2))
    print((args.out_dir/'MODEL_COMPARISON.csv').read_text())


if __name__ == '__main__':
    main()
