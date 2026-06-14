import numpy as np

from quantum_portfolio_optimizer.qubo import PortfolioQUBO, index_to_asset_bits


def test_exact_solution_respects_budget():
    qubo = PortfolioQUBO(
        expected_returns=np.array([0.10, 0.20, 0.05]),
        covariance=np.eye(3) * 0.02,
        budget=2,
    )

    solutions = qubo.exact_solutions(limit=5)

    assert solutions
    assert all(metrics["selected"] == 2 for _, metrics in solutions)


def test_penalty_makes_wrong_cardinality_expensive():
    qubo = PortfolioQUBO(
        expected_returns=np.array([0.10, 0.20, 0.05]),
        covariance=np.eye(3) * 0.02,
        budget=2,
        cardinality_penalty=5.0,
    )

    assert qubo.energy("111") > qubo.energy("110")


def test_index_to_asset_bits_uses_asset_order():
    assert index_to_asset_bits(5, 4) == "1010"

