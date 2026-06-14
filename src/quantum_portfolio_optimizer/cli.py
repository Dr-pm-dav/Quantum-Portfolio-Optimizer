from __future__ import annotations

import argparse
from pathlib import Path

from .data import load_assets
from .qaoa import build_qaoa_circuit, random_search_qaoa, ranked_bitstrings, uniform_expected_energy
from .qubo import PortfolioQUBO
from .reports import plot_distribution, write_csv, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solve a small portfolio QUBO with a Qiskit QAOA circuit.")
    parser.add_argument("--assets", default="data/assets.csv", help="CSV with symbol, expected_return, volatility, and sector columns.")
    parser.add_argument("--budget", type=int, default=3, help="Number of assets to select.")
    parser.add_argument("--risk-aversion", type=float, default=1.4, help="Penalty strength for portfolio variance.")
    parser.add_argument("--trials", type=int, default=160, help="Random QAOA parameter trials.")
    parser.add_argument("--depth", type=int, default=1, help="QAOA depth p.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    parser.add_argument("--out", default="artifacts", help="Directory for generated reports.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    assets_path = Path(args.assets)
    universe = load_assets(assets_path)
    qubo = PortfolioQUBO(
        expected_returns=universe.expected_returns,
        covariance=universe.covariance,
        budget=args.budget,
        risk_aversion=args.risk_aversion,
    )

    result = random_search_qaoa(qubo, depth=args.depth, trials=args.trials, seed=args.seed)
    top_quantum = ranked_bitstrings(qubo, result.distribution, limit=12)
    exact = qubo.exact_solutions(limit=5)
    circuit = build_qaoa_circuit(qubo, result.gammas, result.betas)

    out_dir = Path(args.out)
    write_csv(out_dir / "top_quantum_portfolios.csv", _decorate_rows(top_quantum, universe.symbols))
    plot_distribution(out_dir / "portfolio_distribution.png", top_quantum)
    write_json(
        out_dir / "summary.json",
        {
            "asset_symbols": universe.symbols,
            "budget": args.budget,
            "qaoa_depth": args.depth,
            "qaoa_trials": args.trials,
            "best_gammas": result.gammas,
            "best_betas": result.betas,
            "best_measured_bitstring": result.best_bitstring,
            "best_measured_assets": _assets_from_bitstring(result.best_bitstring, universe.symbols),
            "qaoa_expected_energy": result.expected_energy,
            "uniform_random_expected_energy": uniform_expected_energy(qubo),
            "exact_best": [
                {"bitstring": bitstring, "assets": _assets_from_bitstring(bitstring, universe.symbols), **metrics}
                for bitstring, metrics in exact
            ],
            "circuit": {
                "num_qubits": circuit.num_qubits,
                "depth": circuit.depth(),
                "operations": dict(circuit.count_ops()),
            },
        },
    )

    print(f"Wrote reports to {out_dir.resolve()}")
    print(f"Best measured portfolio: {result.best_bitstring} -> {_assets_from_bitstring(result.best_bitstring, universe.symbols)}")
    print(f"Best exact feasible portfolio: {exact[0][0]} -> {_assets_from_bitstring(exact[0][0], universe.symbols)}")


def _assets_from_bitstring(bitstring: str, symbols: tuple[str, ...]) -> list[str]:
    return [symbol for bit, symbol in zip(bitstring, symbols) if bit == "1"]


def _decorate_rows(rows: list[dict], symbols: tuple[str, ...]) -> list[dict]:
    decorated = []
    for row in rows:
        decorated.append({**row, "assets": ", ".join(_assets_from_bitstring(str(row["bitstring"]), symbols))})
    return decorated


if __name__ == "__main__":
    main()

