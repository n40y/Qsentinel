# quantum/qpe.py  — imports

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import random_unitary
from math import pi, gcd
from typing import Tuple, Optional
import numpy as np


# Implémente l'algorithme de Quantum Phase Estimation (QPE).
def qpe(
    unitary: QuantumCircuit,
    n_qubits: int = 3,
    shots: int = 1024,
    verbose: bool = False,
) -> Tuple[dict, Optional[QuantumCircuit]]:
    t = n_qubits
    qc = QuantumCircuit(t + 1, t)

    qc.x(t)

    for i in range(t):
        qc.h(i)

    for j in range(t):
        for _ in range(2**j):
            qc.append(unitary.to_gate(), [t] + [i for i in range(j, t)])

    for i in range(t // 2):
        qc.swap(i, t - 1 - i)
    for j in range(t):
        for k in range(j):
            qc.cp(-pi / (2 ** (j - k)), k, j)
        qc.h(j)

    qc.measure(range(t), range(t))

    if verbose:
        print("Circuit QPE:")
        print(qc.draw())

    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()

    most_frequent = max(counts, key=counts.get)
    phase_int = int(most_frequent, 2)
    phase = phase_int / (2**t)

    return {
        "phase_estimated": phase,
        "phase_int": phase_int,
        "counts": counts,
        "n_qubits": t,
        "shots": shots,
        "circuit": qc if verbose else None,
    }, qc if verbose else None
