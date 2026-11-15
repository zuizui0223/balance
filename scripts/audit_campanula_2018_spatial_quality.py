#!/usr/bin/env python3
"""Spatial holdout and independently tabulated single-visit proxy, one taxon.

Exploratory post-publication source-bound reanalysis. No causal effect, new
biological replication, or V4 architecture outcome is derived here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT / 'data/external/campanula_2018/single_visit_seedset118.csv'
SEED_SHA256 = '4660d1d49a0d0bb4ad9e3ecc14048bbc40138fe3e5f88ab76c7c966484501cf8'
ORIGINAL_WORKBOOK_SHA256 = 'b81b77248b75330049e1ddd8ae026db127f838e979620a0415a5addb9a7e8f27'
FIELDS = ['FlwID', 'Site', 'Date', 'Pollinator', 'PlantSourcePop', 'Seeds']
GROUPS = ('B', 'M', 'H')  # Bumblebee, Megachile campanulae, small (halictid) bees
GEO_BUFFER_KM = 250.0


def original_module():
    spec = importlib.util.spec_from_file_location(
        'campanula_2018_original_visits', ROOT/'scripts/analyze_campanula_2018_visitation.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_single_visits(path: Path = SEED_FILE):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SEED_SHA256:
        raise ValueError('Single-visit source SHA256 mismatch')
    reader = csv.DictReader(raw.decode('utf-8').splitlines())
    if reader.fieldnames != FIELDS:
        raise ValueError('Single-visit source columns changed')
    rows = list(reader)
    if len(rows) != 118 or len({r['FlwID'] for r in rows}) != 118:
        raise ValueError('Single-visit source must retain 118 distinct flowers')
    if any(r['Pollinator'] not in GROUPS for r in rows):
        raise ValueError('Single-visit source pollinator code changed')
    for row in rows:
        if any(not row[k] for k in FIELDS):
            raise ValueError('Missing single-visit source field')
        try:
            row['Seeds'] = float(row['Seeds'])
            int(row['FlwID']); int(row['Date'])
        except (ValueError, TypeError) as exc:
            raise ValueError('Malformed single-visit seed/ID value') from exc
        if not math.isfinite(row['Seeds']) or row['Seeds'] < 0:
            raise ValueError('Invalid original single-visit seeds')
    if seed_counts(rows) != {'B': 31, 'M': 54, 'H': 33}:
        raise ValueError('Original group sample-size support changed')
    return rows


def seed_counts(rows):
    counts = Counter(r['Pollinator'] for r in rows)
    return {group: counts[group] for group in GROUPS}


def seed_weights(rows):
    return [sum(r['Seeds'] for r in rows if r['Pollinator'] == group) /
            sum(r['Pollinator'] == group for r in rows) for group in GROUPS]


def site_counts(rows):
    return {grp: dict(sorted(Counter(r['Site'] for r in rows
                                    if r['Pollinator'] == grp).items())) for grp in GROUPS}


def make_group_splits(labels):
    import numpy as np
    labs = np.array(list(labels))
    if len(labs) == 0:
        raise ValueError('Empty grouped holdout')
    return [(np.where(labs != z)[0], np.where(labs == z)[0]) for z in sorted(set(labs))]


def buffered_splits(coordinates, radius_km=GEO_BUFFER_KM):
    import numpy as np
    coord = np.asarray(coordinates, float)
    if coord.ndim != 2 or coord.shape[1] != 2 or not np.isfinite(coord).all():
        raise ValueError('Valid latitude/longitude pairs required')
    if np.any(np.abs(coord[:, 0]) > 90) or np.any(np.abs(coord[:, 1]) > 180):
        raise ValueError('Invalid latitude/longitude bounds')
    if not 0 < radius_km < 20000:
        raise ValueError('Invalid buffer radius')
    c = np.deg2rad(coord)
    la, lo = c[:, 0], c[:, 1]
    h = (np.sin((la[:, None] - la[None, :]) / 2) ** 2 +
         np.cos(la[:, None]) * np.cos(la[None, :]) *
         np.sin((lo[:, None] - lo[None, :]) / 2) ** 2)
    distance = 2 * 6371.0088 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
    return [(np.where(distance[i] > radius_km)[0], np.array([i]))
            for i in range(len(coord))]


def quantile_splits(values, n_bins=4):
    import numpy as np
    x = np.asarray(values, float)
    if not np.isfinite(x).all() or len(x) < n_bins:
        raise ValueError('Invalid geographic quantile split')
    order = np.lexsort((np.arange(len(x)), x))
    groups = np.empty(len(x), dtype=int)
    groups[order] = np.arange(len(x)) // math.ceil(len(x) / n_bins)
    return make_group_splits(groups)


def cv_predict(X, y, splits):
    import numpy as np
    design = np.asarray(X, float)
    outcome = np.asarray(y, float)
    if design.ndim != 2 or outcome.ndim != 1 or design.shape[0] != len(outcome):
        raise ValueError('Mismatched cross-validation rows')
    if not np.isfinite(design).all() or not np.isfinite(outcome).all():
        raise ValueError('Cross-validation data must be finite')
    n = len(outcome)
    predicted = np.full(n, np.nan)
    train_count = np.zeros(n, dtype=int)
    seen = np.zeros(n, dtype=int)
    for train, test in splits:
        train = np.asarray(train, int); test = np.asarray(test, int)
        if len(set(train.tolist())) != len(train) or len(set(test.tolist())) != len(test):
            raise ValueError('Repeated train/test row in one fold')
        if not len(test) or len(train) <= design.shape[1]:
            raise ValueError('Holdout design is not estimable')
        if (np.any(train < 0) or np.any(test < 0) or np.any(train >= n) or
                np.any(test >= n) or np.intersect1d(train, test).size):
            raise ValueError('Overlapping or out-of-range train/test indices')
        if np.linalg.matrix_rank(design[train]) != design.shape[1]:
            raise ValueError('Holdout training design rank deficient')
        beta = np.linalg.lstsq(design[train], outcome[train], rcond=None)[0]
        predicted[test] = design[test] @ beta
        train_count[test] = len(train)
        seen[test] += 1
    if not np.all(seen == 1) or not np.isfinite(predicted).all():
        raise ValueError('Cross-validation must predict each original population once')
    return predicted, train_count


def analyze():
    import numpy as np
    original = original_module()
    population = original.load_population()  # source SHA256 + original sample gate
    visits = load_single_visits()              # separate source SHA256 + 118 flower gate
    n = len(population)
    rates = np.array([[row[k] for k in original.RATE_FIELDS] for row in population], float)
    y = np.sqrt(np.array([row['Pollen Limitation 2016'] for row in population], float))
    coords = np.array([[row['Latitude'], row['Longitude']] for row in population], float)
    totals = rates.sum(axis=1)
    shares = rates / totals[:, None]
    raw_weights = np.asarray(seed_weights(visits), float)
    weights = raw_weights / raw_weights[0]  # bumblebee-normalized effective-visit units
    qvisits = np.sum(rates * weights[None, :], axis=1)
    designs = {
        'total': np.column_stack([np.ones(n), np.log(totals + .1)]),
        'total_plus_composition': np.column_stack([np.ones(n), np.log(totals + .1), shares[:, 1:]]),
        'three_group_rates': np.column_stack([np.ones(n), np.log(rates + .1)]),
        'single_visit_seedset_weighted': np.column_stack([np.ones(n), np.log(qvisits + .1)]),
    }
    strategies = {
        'LOO': make_group_splits(np.arange(n)),
        'state': make_group_splits([row['Population'].split('_', 1)[0] for row in population]),
        'latitudinal_4_blocks': quantile_splits(coords[:, 0]),
        'longitudinal_4_blocks': quantile_splits(coords[:, 1]),
        'buffer_250km': buffered_splits(coords),
    }
    cv = {}; store = {}
    for method, splits in strategies.items():
        cv[method] = {'fold_count': len(splits), 'models': {}}
        store[method] = {}
        for label, X in designs.items():
            prediction, train_counts = cv_predict(X, y, splits)
            delta = prediction - y
            cv[method]['models'][label] = {
                'rmse': float(np.sqrt(np.mean(delta ** 2))),
                'mae': float(np.mean(np.abs(delta))),
            }
            store[method][label] = prediction
        cv[method]['train_min'] = min(len(train) for train, test in splits)
        cv[method]['train_max'] = max(len(train) for train, test in splits)
    win_state = 0
    states = [row['Population'].split('_', 1)[0] for row in population]
    for state in sorted(set(states)):
        mask = np.array([s == state for s in states])
        reduced = np.mean((store['state']['total'][mask] - y[mask]) ** 2)
        full = np.mean((store['state']['total_plus_composition'][mask] - y[mask]) ** 2)
        if full < reduced:
            win_state += 1
    predictions = []
    for i, row in enumerate(population):
        predictions.append({
            'population': row['Population'], 'state': states[i],
            'observed_sqrt_PL': float(y[i]),
            'state_holdout_train_count': len(next(train for train, test in strategies['state'] if i in test)),
            '250km_buffer_train_count': len(strategies['buffer_250km'][i][0]),
            'models': {label: {
                'state_pred': float(store['state'][label][i]),
                'buffer_250km_pred': float(store['buffer_250km'][label][i])}
                for label in designs},
        })
    state=cv['state']['models']; buffer=cv['buffer_250km']['models']
    return {
        'schema': 'BALANCE_CAMPANULA_2018_SPATIAL_QUALITY_V1',
        'status': 'POST_PUBLICATION_WITHIN_SPECIES_EXPLORATORY_NOT_CONFIRMATORY',
        'population_count': n, 'state_count': len(set(states)), 'original_plant_species': 1,
        'original_population_csv_sha256': original.CSV_SHA256,
        'seed_visit_csv_sha256': SEED_SHA256,
        'original_workbook_sha256': ORIGINAL_WORKBOOK_SHA256,
        'seed_visit_counts': seed_counts(visits),
        'seed_means_B_M_H': {k: float(v) for k, v in zip(GROUPS, raw_weights)},
        'seed_relative_weights_B_M_H': {k: float(v) for k, v in zip(GROUPS, weights)},
        'seed_visit_sites_B_M_H': site_counts(visits),
        'source_quality_site_confounded': True,
        'CV_per_pop_across_all_groups': True,
        'CV_geography_only_internal_not_external': True,
        'state_wins_for_composition': win_state,
        'state_composition_rmse_reduction_relative_to_total': 1-state['total_plus_composition']['rmse']/state['total']['rmse'],
        'buffer250_composition_rmse_reduction_relative_to_total': 1-buffer['total_plus_composition']['rmse']/buffer['total']['rmse'],
        'cv': cv,
        'population_predictions': predictions,
        'structural_architecture_fitness_identified': False,
        'global_floral_prevalence_inferred': False,
        'V4_inputs_modified': False,
        'interpretation_limit': [
            'Within one species and previously published data; states are administrative geographic blocks, not biological replicates.',
            'Site-of-assay severely differs among pollinator classes; per-visit raw means do not isolate intrinsic class efficiency.',
            'Quality-weighting assumes a linear additive single-visit seed production contribution; seed saturation and sex-phase bias are omitted.',
            'Each geographic validation is internal and uses overlapping training data; no independent-region or independent-species prospective validation.',
            'Exploratory model comparisons; 250 km buffer and 4-block geographic partitions are sensitivity tests, not preregistered discoveries.',
            'Neither population visitation nor cross-class source data randomizes pollinator composition; all effects are associative.',
            'Original V4 human source-blinded architecture coding and entire source-admission denominator remain untouched.'
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    receipt = analyze()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    (args.out_dir / 'SPATIAL_QUALITY_RESULTS.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    with (args.out_dir / 'CV_COMPARISON.csv').open('w', newline='', encoding='utf-8') as f:
        out = csv.writer(f)
        out.writerow(['holdout','model','n','fold_count','train_min','rmse_sqrtPL','mae_sqrtPL'])
        for name, group in receipt['cv'].items():
            for model, stats in group['models'].items():
                out.writerow([name, model, receipt['population_count'], group['fold_count'],
                              group['train_min'], stats['rmse'], stats['mae']])
    print(json.dumps({'states': receipt['state_count'], 'state_composition_reduction': receipt['state_composition_rmse_reduction_relative_to_total'],
                      'buffer250_composition_reduction': receipt['buffer250_composition_rmse_reduction_relative_to_total'],
                      'state_wins': receipt['state_wins_for_composition'],
                      'seed_visit_site_counts': receipt['seed_visit_sites_B_M_H']}, indent=2))


if __name__ == '__main__':
    main()
