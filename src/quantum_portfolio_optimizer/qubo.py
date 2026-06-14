from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np


@dataclass(frozen=True)
class PortfolioQUBO:
    expected_returns: np.ndarray
    covariance: np.ndarray
    budget: int
    risk_aversion: float = 1.4
    return_weight: float = 1.0
    cardinality_penalty: float = 2.0

    @property
    def n_assets(self) -> int:
        return int(self.expected_returns.shape[0])

    def energy(self, bits: str | tuple[int, ...] | list[int] | np.ndarray) -> float:
        x = np.array([int(bit) for bit in bits], dtype=float)
        variance = float(x @ self.covariance @ x)
        expected_return = float(self.expected_returns @ x)
        budget_penalty = float((x.sum() - self.budget) ** 2)
        return (
            self.risk_aversion * variance
            - self.return_weight * expected_return
            + self.cardinality_penalty * budget_penalty
        )

    def portfolio_metrics(self, bits: str | tuple[int, ...]) -> dict[str, float | int]:
        x = np.array([int(bit) for bit in bits], dtype=float)
        expected_return = float(self.expected_returns @ x)
        variance = float(x @ self.covariance @ x)
        risk = float(np.sqrt(max(variance, 0.0)))
        return {
            "selected": int(x.sum()),
            "expected_return": expected_return,
            "risk": risk,
            "score": expected_return - self.risk_aversion * variance,
            "energy": self.energy(bits),
        }

    def exact_solutions(self, limit: int = 10) -> list[tuple[str, dict[str, float | int]]]:
        candidates: list[tuple[str, dict[str, float | int]]] = []
        for bits in product((0, 1), repeat=self.n_assets):
            if sum(bits) != self.budget:
                continue
            bitstring = "".join(str(bit) for bit in bits)
            candidates.append((bitstring, self.portfolio_metrics(bitstring)))

        candidates.sort(key=lambda item: (float(item[1]["energy"]), -float(item[1]["score"])))
        return candidates[:limit]


def index_to_asset_bits(index: int, n_assets: int) -> str:
    return "".join(str((index >> asset_index) & 1) for asset_index in range(n_assets))


def all_asset_bitstrings(n_assets: int) -> list[str]:
    return [index_to_asset_bits(index, n_assets) for index in range(2**n_assets)]

