# quantum/grover.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from math import isqrt, pi


def oracle(qc: QuantumCircuit, target: str) -> None:
    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)
    qc.h(len(target) - 1)
    qc.mcx(list(range(len(target) - 1)), len(target) - 1)
    qc.h(len(target) - 1)
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)


def diffuser(qc: QuantumCircuit, n_qubits: int) -> None:
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))


def grover(target: str, shots: int = 1024) -> dict:
    n = len(target)
    n_iterations = max(1, round((pi / 4) * (2 ** (n / 2))))
    if n <= 3:
        n_iterations = 1

    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    for _ in range(n_iterations):
        oracle(qc, target)
        diffuser(qc, n)

    qc.measure(range(n), range(n))
    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    counts_sorted = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    top = list(counts_sorted.items())[0]

    return {
        "target": target,
        "n_qubits": n,
        "n_iterations": n_iterations,
        "top_result": top[0],
        "top_probability": round(top[1] / shots, 3),
        "found": top[0] == target,
        "counts": counts_sorted,
    }


def estimate_quantum_time(results: dict) -> dict:
    """Impact de Grover sur le chiffrement AES."""
    tls = results.get("tls", {})
    cipher_suites = tls.get("cipher_suites", [])

    aes128 = any("AES_128" in cs for cs in cipher_suites)
    aes256 = any("AES_256" in cs for cs in cipher_suites)

    return {
        "grover_impact": {
            "AES-128": "64 bits effectifs (cassable)" if aes128 else "non détecté",
            "AES-256": "128 bits effectifs (sûr)" if aes256 else "non détecté",
        },
        "recommendation": "Migrer vers AES-256 minimum" if aes128 else "AES OK",
    }
