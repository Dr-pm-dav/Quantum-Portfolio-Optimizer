import numpy as np

from quantum_portfolio_optimizer.qaoa import build_qaoa_circuit, expected_energy, random_search_qaoa, simulate_distribution
from quantum_portfolio_optimizer.qubo import PortfolioQUBO


def tiny_qubo() -> PortfolioQUBO:
    return PortfolioQUBO(
        expected_returns=np.array([0.10, 0.16, 0.08]),
        covariance=np.array(
            [
                [0.030, 0.004, 0.002],
                [0.004, 0.060, 0.003],
                [0.002, 0.003, 0.020],
            ]
        ),
        budget=2,
    )


def test_qaoa_distribution_is_normalized():
    circuit = build_qaoa_circuit(tiny_qubo(), gammas=(0.8,), betas=(0.4,))
    distribution = simulate_distribution(circuit)

    assert abs(sum(distribution.values()) - 1.0) < 1e-9


def test_expected_energy_matches_distribution_weighting():
    qubo = tiny_qubo()
    distribution = {"000": 0.25, "110": 0.75}

    assert expected_energy(qubo, distribution) == 0.25 * qubo.energy("000") + 0.75 * qubo.energy("110")


def test_random_search_returns_valid_result():
    qubo = tiny_qubo()
    result = random_search_qaoa(qubo, trials=5, seed=1)

    assert len(result.best_bitstring) == qubo.n_assets
    assert result.expected_energy < 10.0

