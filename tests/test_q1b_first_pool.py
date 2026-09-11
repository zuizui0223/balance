import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GYM = ROOT / 'data' / 'BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json'
IMP = ROOT / 'data' / 'BALANCE_IMPATIENS_Q1B_CLUSTER_AGGREGATE_V1.json'
POOL = ROOT / 'data' / 'BALANCE_Q1B_FIRST_POOL_V1.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def test_gymnadenia_is_third_effect_ready_positive():
    g = load(GYM)
    assert g['effect_size_status'].startswith('EFFECT_SIZE_READY')
    assert g['q1b_positive_point_pattern'] is True
    assert g['mediated_contrasts'][0] > 0
    assert g['mediated_contrasts'][1] > 0
    assert g['mediated_contrasts'][2] < 0
    assert g['mediated_contrasts'][3] < 0
    assert len(g['contrast_covariance']) == 4
    assert 'not direct BALANCE' in g['claim_ceiling']


def test_impatiens_is_one_cluster_not_two_traits():
    i = load(IMP)
    assert i['effect_size_status'] == 'EFFECT_SIZE_READY_CLUSTER_AGGREGATE'
    assert i['aggregation_rule'] == 'equal_weight_mean_across_all_predeclared_traits'
    assert len(i['traits']) == 2
    assert len(i['mediated_contrasts']) == 4


def test_first_pool_contains_exactly_three_independent_clusters():
    p = load(POOL)
    assert p['pool_gate'] == 'OPEN_3_OF_3_EFFECT_SIZE_READY_POSITIVE_CLUSTERS'
    assert p['independent_clusters'] == 3
    assert p['cluster_names'] == ['Fragaria', 'Impatiens', 'Gymnadenia']
    assert len(set(p['cluster_names'])) == 3
    assert len(p['pooled']) == 4
    for result in p['pooled'].values():
        assert result['k'] == 3
        lo, hi = result['ci95_mkh']
        assert lo <= result['mu_random'] <= hi
    assert 'does not identify direct BALANCE occupancy' in p['claim_ceiling']
    assert 'do not count Impatiens traits as independent clusters' in p['prohibited']


def test_first_pool_is_small_k_and_not_a_strong_mean_effect_claim():
    p = load(POOL)
    assert all(result['ci95_mkh'][0] < 0 < result['ci95_mkh'][1] for result in p['pooled'].values())
