"""Source integrity and optional numerical regressions for one plant species."""
import csv
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/analyze_campanula_2018_visitation.py'
SOURCE = ROOT / 'data/external/campanula_2018/population23.csv'


def module():
    spec = importlib.util.spec_from_file_location('campanula_visitation', SCRIPT)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_exact_original_23_population_extract():
    rows = module().load_population(SOURCE)
    assert len(rows) == 23
    assert len({r['Population'] for r in rows}) == 23
    assert sum(r['Pollen Limitation 2016'] == 0 for r in rows) == 2


def test_modified_source_cannot_silently_enter(tmp_path):
    file = tmp_path / 'changed.csv'
    file.write_bytes(SOURCE.read_bytes().replace(b'0.146895273', b'0.946895273'))
    with pytest.raises(ValueError, match='checksum'):
        module().load_population(file)


@pytest.mark.parametrize('change,message', [
    ('duplicate', 'distinct'), ('negative', 'nonnegative'),
    ('nan', 'finite'), ('zero', 'positive total'), ('missing', 'numeric')])
def test_malformed_population_rejected(change, message):
    m = module()
    rows = m.load_population(SOURCE)
    if change == 'duplicate':
        rows[1]['Population'] = rows[0]['Population']
    elif change == 'negative':
        rows[0]['Small Rate'] = -1
    elif change == 'nan':
        rows[0]['Small Rate'] = float('nan')
    elif change == 'zero':
        for k in m.RATE_FIELDS:
            rows[0][k] = 0
    else:
        rows[0]['Pollen Limitation 2016'] = None
    with pytest.raises(ValueError, match=message):
        m.validate_population(rows)


def test_numerical_result_and_prespecified_sensitivities():
    pytest.importorskip('numpy')
    pytest.importorskip('statsmodels.api')
    m = module()
    result = m.analyze(m.load_population(SOURCE))
    models = result['outcomes']['sqrt_archived_PL']
    assert models['three_visitor_rates']['r2'] == pytest.approx(0.6296, abs=0.0001)
    assert models['total_visits']['r2'] == pytest.approx(0.1035, abs=0.0001)
    assert models['total_and_composition']['loocv_rmse'] == pytest.approx(0.18308802475)
    assert result['archived_PL_zero_count'] == 2
    assert result['independent_plant_species'] == 1
    assert result['causal_architecture_test'] is False
    assert len(result['outcomes']['archived_PL']) == 7
    assert models['total_and_composition']['parameter_count_with_variance'] == 5
    small = models['total_and_composition']['coefficients'][3]
    assert small['name'] == 'small_fraction'
    assert small['loo_positive'] == 23
    assert small['estimate'] == pytest.approx(0.758660941561)


def test_loocv_matches_independent_direct_refits():
    np = pytest.importorskip('numpy')
    pytest.importorskip('statsmodels.api')
    m = module()
    x = np.arange(1.0, 12.0)
    y = x + np.sin(x)
    result = m.fit_summary(y, x[:, None], ['x'])
    X = np.column_stack([np.ones(len(x)), x])
    errors = []
    for j in range(len(x)):
        keep = np.arange(len(x)) != j
        beta = np.linalg.lstsq(X[keep], y[keep], rcond=None)[0]
        errors.append(y[j] - X[j] @ beta)
    assert result['loocv_rmse'] == pytest.approx(np.sqrt(np.mean(np.square(errors))))


def test_rank_deficient_design_rejected():
    np = pytest.importorskip('numpy')
    pytest.importorskip('statsmodels.api')
    with pytest.raises(ValueError, match='rank'):
        module().fit_summary(np.arange(12.0), np.ones((12, 2)), ['a', 'b'])
