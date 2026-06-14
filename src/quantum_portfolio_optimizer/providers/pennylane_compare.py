from __future__ import annotations

import numpy as np

from quantum_portfolio_optimizer.qubo import PortfolioQUBO, index_to_asset_bits


def qaoa_probabilities_pennylane(
    qubo: PortfolioQUBO,
    gammas: tuple[float, ...],
    betas: tuple[float, ...],
) -> dict[str, float]:
    """Recreate the QAOA ansatz with Xanadu PennyLane's default.qubit simulator."""

    import pennylane as qml

    if len(gammas) != len(betas):
        raise ValueError("QAOA needs the same number of gamma and beta parameters.")

    n_assets = qubo.n_assets
    dev = qml.device("default.qubit", wires=n_assets)

    @qml.qnode(dev)
    def circuit() -> np.ndarray:
        for wire in range(n_assets):
            qml.Hadamard(wires=wire)

        for gamma, beta in zip(gammas, betas):
            diagonal = np.array(
                [np.exp(-1j * gamma * qubo.energy(index_to_asset_bits(index, n_assets))) for index in range(2**n_assets)],
                dtype=complex,
            )
            qml.DiagonalQubitUnitary(diagonal, wires=range(n_assets))
            for wire in range(n_assets):
                qml.RX(2.0 * beta, wires=wire)

        return qml.probs(wires=range(n_assets))

    probabilities = circuit()
    return {
        index_to_asset_bits(index, n_assets): float(probability)
        for index, probability in enumerate(probabilities)
        if probability > 1e-12
    }

