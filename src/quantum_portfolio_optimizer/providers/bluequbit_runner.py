from __future__ import annotations

import os
from typing import Any

from qiskit import QuantumCircuit


def run_with_bluequbit(
    circuit: QuantumCircuit,
    device: str = "mps.cpu",
    job_name: str = "quantum-portfolio-optimizer",
    token: str | None = None,
    **options: Any,
) -> Any:
    """Submit a Qiskit circuit to BlueQubit.

    BlueQubit's SDK accepts Qiskit circuits directly, so this adapter keeps the
    project circuit portable while leaving account-specific setup outside git.
    """

    import bluequbit

    client = bluequbit.init(token or os.getenv("BLUEQUBIT_TOKEN"))
    run_kwargs: dict[str, Any] = {"device": device, "job_name": job_name}
    if options:
        run_kwargs["options"] = options
    return client.run(circuit, **run_kwargs)
