from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

from .qubo import PortfolioQUBO, all_asset_bitstrings, index_to_asset_bits


@dataclass(frozen=True)
class QAOAResult:
    gammas: tuple[float, ...]
    betas: tuple[float, ...]
    expected_energy: float
    distribution: dict[str, float]

    @property
    def best_bitstring(self) -> str:
        return max(self.distribution, key=self.distribution.get)


def build_qaoa_circuit(qubo: PortfolioQUBO, gammas: tuple[float, ...], betas: tuple[float, ...]) -> QuantumCircuit:
    if len(gammas) != len(betas):
        raise ValueError("QAOA needs the same number of gamma and beta parameters.")

    circuit = QuantumCircuit(qubo.n_assets, name="portfolio_qaoa")
    circuit.h(range(qubo.n_assets))

    for gamma, beta in zip(gammas, betas):
        phases = [np.exp(-1j * gamma * qubo.energy(index_to_asset_bits(index, qubo.n_assets))) for index in range(2**qubo.n_assets)]
        circuit.append(DiagonalGate(phases), range(qubo.n_assets))
        for qubit in range(qubo.n_assets):
            circuit.rx(2.0 * beta, qubit)

    return circuit


def simulate_distribution(circuit: QuantumCircuit) -> dict[str, float]:
    state = Statevector.from_instruction(circuit)
    probabilities = state.probabilities()
    n_assets = circuit.num_qubits
    return {
        index_to_asset_bits(index, n_assets): float(probability)
        for index, probability in enumerate(probabilities)
        if probability > 1e-12
    }


def expected_energy(qubo: PortfolioQUBO, distribution: dict[str, float]) -> float:
    return float(sum(probability * qubo.energy(bitstring) for bitstring, probability in distribution.items()))


def random_search_qaoa(
    qubo: PortfolioQUBO,
    depth: int = 1,
    trials: int = 160,
    seed: int = 7,
) -> QAOAResult:
    rng = np.random.default_rng(seed)
    best: QAOAResult | None = None

    for _ in range(trials):
        gammas = tuple(float(value) for value in rng.uniform(0.0, np.pi, size=depth))
        betas = tuple(float(value) for value in rng.uniform(0.0, np.pi / 2.0, size=depth))
        circuit = build_qaoa_circuit(qubo, gammas, betas)
        distribution = simulate_distribution(circuit)
        energy = expected_energy(qubo, distribution)
        if best is None or energy < best.expected_energy:
            best = QAOAResult(gammas, betas, energy, distribution)

    if best is None:
        raise ValueError("trials must be greater than zero.")
    return best


def ranked_bitstrings(qubo: PortfolioQUBO, distribution: dict[str, float], limit: int = 10) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for bitstring, probability in distribution.items():
        row = {"bitstring": bitstring, "probability": probability}
        row.update(qubo.portfolio_metrics(bitstring))
        rows.append(row)

    rows.sort(key=lambda row: (-float(row["probability"]), float(row["energy"])))
    return rows[:limit]


def uniform_expected_energy(qubo: PortfolioQUBO) -> float:
    probability = 1.0 / (2**qubo.n_assets)
    return float(sum(probability * qubo.energy(bits) for bits in all_asset_bitstrings(qubo.n_assets)))

