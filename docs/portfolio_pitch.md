# Portfolio Pitch

## Project title

Quantum Portfolio Optimizer

## One-line pitch

A local-first quantum optimization demo that turns asset selection into a QUBO, searches it with a Qiskit QAOA circuit, and includes optional adapters for IBM Quantum, BlueQubit, and Xanadu PennyLane.

## Why it belongs in a portfolio

- It shows practical quantum-computing fluency without pretending current hardware guarantees financial advantage.
- It combines optimization, simulation, cloud-provider awareness, and clean Python package structure.
- It includes exact classical baselines, which makes the quantum result interpretable instead of theatrical.
- It is small enough to demo in an interview and structured enough to extend into real research.

## Extension ideas

- Replace the synthetic covariance model with historical returns from a market-data API.
- Add noisy simulation and compare ideal, noisy, and hardware-sampled distributions.
- Swap random parameter search for a scipy optimizer or SPSA loop.
- Add a Streamlit dashboard for asset selection, risk controls, and result visualization.

