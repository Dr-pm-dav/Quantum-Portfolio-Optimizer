# Quantum Portfolio Optimizer

A portfolio-ready quantum computing project built with **IBM Qiskit**. It models asset selection as a QUBO, solves the small instance exactly as a classical baseline, then uses a QAOA-style quantum circuit to search for low-energy portfolios.

The project is local-first: it runs with Qiskit statevector simulation out of the box. Optional adapters show how the same Qiskit circuit can move toward IBM Quantum Runtime, BlueQubit cloud simulation, or Xanadu PennyLane validation.

## What It Demonstrates

- QUBO modeling for a constrained optimization problem.
- QAOA circuit construction in Qiskit.
- Exact classical baseline comparison.
- Portfolio metrics: expected return, risk, score, energy, and measurement probability.
- Optional provider integrations for IBM Quantum, BlueQubit, and PennyLane.

## Architecture

```text
data/assets.csv
  -> load asset returns and volatility assumptions
  -> build a mean-variance QUBO with a cardinality penalty
  -> run Qiskit QAOA statevector simulation
  -> rank measured bitstrings as candidate portfolios
  -> write CSV, JSON, and PNG reports
```

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m quantum_portfolio_optimizer.cli --trials 200 --depth 1
pytest
```

Generated reports appear in `artifacts/`:

- `summary.json`: QAOA parameters, circuit stats, exact baseline, and best measured portfolio.
- `top_quantum_portfolios.csv`: ranked bitstrings and portfolio metrics.
- `portfolio_distribution.png`: probability chart for leading candidates.

## Example Interpretation

Each bitstring maps left-to-right to the assets in `data/assets.csv`.

For example, with the default sample data:

```text
101001 -> NVDA, MSFT, NEE
```

The exact solver ranks feasible portfolios with exactly three selected assets. QAOA ranks candidates by measurement probability, and the QUBO penalty helps push probability mass toward feasible portfolios.

## Optional Cloud Paths

### IBM Quantum

IBM Quantum recommends Qiskit for local work and Qiskit Runtime primitives for cloud hardware. The adapter in `src/quantum_portfolio_optimizer/providers/ibm_runtime.py` uses `SamplerV2` and loads credentials from:

```powershell
$env:IBM_QUANTUM_TOKEN = "your-token"
$env:IBM_QUANTUM_INSTANCE = "your-instance"  # optional
```

### BlueQubit

BlueQubit accepts Qiskit circuits directly through its Python SDK. The adapter in `providers/bluequbit_runner.py` loads:

```powershell
$env:BLUEQUBIT_TOKEN = "your-token"
```

It defaults to `mps.cpu`, which is useful for larger cloud simulation experiments.

### Xanadu PennyLane

`providers/pennylane_compare.py` recreates the QAOA circuit on PennyLane's `default.qubit` simulator. This is useful for cross-framework validation and as a bridge into Xanadu's quantum machine-learning ecosystem.

Install the optional integrations with:

```powershell
python -m pip install -e ".[cloud,dev]"
```

## Project Story For Interviews

> I built a quantum optimization project around portfolio selection. The core idea is to encode risk, return, and a fixed asset budget into a QUBO, then use a QAOA circuit in Qiskit to search the solution space. I compare the result with an exact solver because small quantum demos should be honest and measurable. I also separated cloud-provider adapters so the circuit can be tested locally first, then moved toward IBM Quantum Runtime, BlueQubit, or PennyLane.

## Source Notes

- IBM Quantum Qiskit installation guide: https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit
- IBM Quantum Runtime primitives guide: https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-primitives
- BlueQubit Python SDK quick start: https://app.bluequbit.io/sdk-docs/index.html
- Xanadu PennyLane product page: https://www.xanadu.ai/products/pennylane/
- PennyLane `default.qubit` device: https://pennylane.ai/devices/default-qubit

