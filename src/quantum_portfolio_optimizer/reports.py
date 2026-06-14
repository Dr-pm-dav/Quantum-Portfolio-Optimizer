from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable


def write_json(path: str | Path, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: str | Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("Cannot write an empty CSV report.")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_distribution(path: str | Path, rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    labels = [str(row["bitstring"]) for row in rows]
    probabilities = [float(row["probability"]) for row in rows]
    colors = ["#1f77b4" if int(row["selected"]) == 3 else "#8c8c8c" for row in rows]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, probabilities, color=colors)
    ax.set_title("QAOA portfolio candidates")
    ax.set_xlabel("Asset-selection bitstring")
    ax.set_ylabel("Measurement probability")
    ax.set_ylim(0, max(probabilities) * 1.2)
    ax.grid(axis="y", alpha=0.24)
    fig.tight_layout()
    fig.savefig(target, dpi=160)
    plt.close(fig)

