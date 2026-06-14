from __future__ import annotations

import os
from typing import Any

from qiskit import QuantumCircuit


def run_with_ibm_sampler(
    circuit: QuantumCircuit,
    shots: int = 4096,
    backend_name: str | None = None,
    token: str | None = None,
    instance: str | None = None,
) -> Any:
    """Run a measured Qiskit circuit with IBM Quantum Runtime SamplerV2.

    This function is intentionally optional. It imports qiskit-ibm-runtime only
    when called so the local simulator project works without cloud credentials.
    """

    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

    service_kwargs: dict[str, str] = {"channel": "ibm_quantum_platform"}
    quantum_token = token or os.getenv("IBM_QUANTUM_TOKEN")
    quantum_instance = instance or os.getenv("IBM_QUANTUM_INSTANCE")
    if quantum_token:
        service_kwargs["token"] = quantum_token
    if quantum_instance:
        service_kwargs["instance"] = quantum_instance
    service = QiskitRuntimeService(**service_kwargs)
    backend = service.backend(backend_name) if backend_name else service.least_busy(operational=True, simulator=False)

    measured = circuit.copy()
    if not measured.cregs:
        measured.measure_all()

    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pass_manager.run(measured)

    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)
    return job.result()
