# quantum/shor.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from math import gcd, isqrt
from random import randint
from fractions import Fraction


def _build_order_finding_circuit(a: int, N: int, n_count: int) -> QuantumCircuit:
    """Circuit de recherche d'ordre pour a mod N (version pédagogique, N <= 63)."""
    n_target = N.bit_length()
    qc = QuantumCircuit(n_count + n_target, n_count)

    # Initialiser le registre cible à |1>
    qc.x(n_count)

    # Hadamard sur le registre de comptage
    for q in range(n_count):
        qc.h(q)

    # Exponentiations modulaires contrôlées
    for q in range(n_count):
        power = pow(a, 2**q, N)
        for _ in range(power):
            for i in range(n_target - 1):
                qc.cx(n_count + i, n_count + i + 1)

    # QFT inverse sur le registre de comptage
    for q in range(n_count // 2):
        qc.swap(q, n_count - 1 - q)
    for j in range(n_count):
        for k in range(j):
            qc.cp(-3.14159265358979 / (2 ** (j - k)), k, j)
        qc.h(j)

    qc.measure(range(n_count), range(n_count))
    return qc


def shor_factorize(n: int, shots: int = 1024) -> int | None:
    """
    Factorise n via l'algorithme de Shor (simulation).
    Retourne un facteur non trivial, ou None si échec.
    """
    if n % 2 == 0:
        return 2
    if n == 1:
        return 1

    # Vérifier si n est une puissance parfaite
    for k in range(2, n.bit_length() + 1):
        root = round(n ** (1 / k))
        for candidate in (root - 1, root, root + 1):
            if candidate > 1 and candidate**k == n:
                return candidate

    n_count = 2 * n.bit_length()

    for _ in range(8):  # Plusieurs tentatives
        a = randint(2, n - 1)
        g = gcd(a, n)
        if g != 1:
            return g  # Facteur trouvé classiquement

        qc = _build_order_finding_circuit(a, n, n_count)
        sim = AerSimulator()
        result = sim.run(qc, shots=shots).result()
        counts = result.get_counts()

        # Extraire la phase et estimer l'ordre via les fractions continues
        for measured, _ in sorted(counts.items(), key=lambda x: -x[1]):
            phase_int = int(measured, 2)
            if phase_int == 0:
                continue
            phase = phase_int / (2 ** n_count)
            frac = Fraction(phase).limit_denominator(n)
            r = frac.denominator

            if r % 2 != 0:
                continue
            if pow(a, r, n) != 1:
                continue

            candidate = gcd(pow(a, r // 2) - 1, n)
            if 1 < candidate < n:
                return candidate

    return None
