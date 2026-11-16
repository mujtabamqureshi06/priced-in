import numpy as np
import pytest

from pricedin.price_models import GBM, flat_deck

N = 200_000


def test_same_seed_same_paths() -> None:
    model = GBM(spot=1800.0, drift=0.01, volatility=0.15)
    a = model.simulate(10, 100, np.random.default_rng(7))
    b = model.simulate(10, 100, np.random.default_rng(7))
    np.testing.assert_array_equal(a, b)


def test_shape_and_spot_column() -> None:
    paths = GBM(1800.0, 0.0, 0.15).simulate(12, 50, np.random.default_rng(1))
    assert paths.shape == (50, 13)
    assert np.all(paths[:, 0] == 1800.0)
    assert np.all(paths > 0)


def test_log_returns_match_target_moments() -> None:
    mu, sigma = 0.02, 0.16
    paths = GBM(1500.0, mu, sigma).simulate(5, N, np.random.default_rng(11))
    r = np.diff(np.log(paths), axis=1)
    se_mean = sigma / np.sqrt(r.size)
    assert r.mean() == pytest.approx(mu - 0.5 * sigma**2, abs=4 * se_mean)
    assert r.std() == pytest.approx(sigma, rel=0.01)


def test_expected_price_grows_at_drift() -> None:
    """E[S_t] = S_0 exp(drift * t): the property risk-neutral valuation relies on."""
    mu, sigma, t = 0.015, 0.18, 10
    paths = GBM(1000.0, mu, sigma).simulate(t, N, np.random.default_rng(3), antithetic=True)
    final = paths[:, -1]
    se = final.std() / np.sqrt(final.size)
    assert final.mean() == pytest.approx(1000.0 * np.exp(mu * t), abs=4 * se)


def test_zero_volatility_is_deterministic() -> None:
    paths = GBM(1000.0, 0.03, 0.0).simulate(4, 3, np.random.default_rng(0))
    np.testing.assert_allclose(paths[0], 1000.0 * np.exp(0.03 * np.arange(5)))


def test_antithetic_pairs_are_mirrored() -> None:
    paths = GBM(1000.0, 0.0, 0.2).simulate(3, 4, np.random.default_rng(5), antithetic=True)
    log_steps = np.diff(np.log(paths), axis=1) + 0.5 * 0.2**2
    np.testing.assert_allclose(log_steps[:2], -log_steps[2:])


def test_standard_error_falls_with_paths() -> None:
    model = GBM(1000.0, 0.0, 0.2)
    se = []
    for n in (1_000, 16_000):
        final = model.simulate(5, n, np.random.default_rng(9))[:, -1]
        se.append(final.std() / np.sqrt(n))
    assert se[1] == pytest.approx(se[0] / 4, rel=0.15)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"spot": 0.0, "drift": 0.0, "volatility": 0.1}, "spot must be positive"),
        ({"spot": 10.0, "drift": 0.0, "volatility": -0.1}, "volatility must be non-negative"),
    ],
)
def test_rejects_bad_parameters(kwargs: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        GBM(**kwargs)


def test_rejects_odd_paths_with_antithetic() -> None:
    with pytest.raises(ValueError, match="must be even"):
        GBM(1.0, 0.0, 0.1).simulate(2, 3, np.random.default_rng(0), antithetic=True)


def test_flat_deck_returns_study_price_exactly() -> None:
    deck = flat_deck(1400.0, 11, 2)
    assert deck.shape == (2, 12)
    assert np.all(deck == 1400.0)
