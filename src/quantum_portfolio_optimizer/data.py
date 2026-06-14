from __future__ import annotations

from dataclasses import dataclass
import csv
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class AssetUniverse:
    symbols: tuple[str, ...]
    expected_returns: np.ndarray
    covariance: np.ndarray
    sectors: tuple[str, ...]


def load_assets(path: str | Path) -> AssetUniverse:
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8")))
    if not rows:
        raise ValueError(f"No assets found in {path}")

    symbols = tuple(row["symbol"] for row in rows)
    sectors = tuple(row.get("sector", "") for row in rows)
    expected_returns = np.array([float(row["expected_return"]) for row in rows], dtype=float)
    volatility = np.array([float(row["volatility"]) for row in rows], dtype=float)
    correlation = _sector_aware_correlation(sectors)
    covariance = np.outer(volatility, volatility) * correlation
    return AssetUniverse(symbols, expected_returns, covariance, sectors)


def _sector_aware_correlation(sectors: tuple[str, ...]) -> np.ndarray:
    n_assets = len(sectors)
    correlation = np.full((n_assets, n_assets), 0.18, dtype=float)
    np.fill_diagonal(correlation, 1.0)

    for i, left in enumerate(sectors):
        for j, right in enumerate(sectors):
            if i != j and left == right:
                correlation[i, j] = 0.42
    return correlation

