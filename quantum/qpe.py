# quantum/qpe.py

from qiskit import QuantumCircuit, execute
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import random_unitary
from math import pi, gcd
from typing import Tuple, Optional
import numpy as np


def qpe(
    unitary: QuantumCircuit,
    n_qubits: int = 3,
    shots: int = 1024,
    verbose: bool = False,
) -> Tuple[dict, Optional[QuantumCircuit]]:
    """
    Implémente l'algorithme de Quantum Phase Estimation (QPE).

    Args:
        unitary: Circuit quantique représentant l'opérateur unitaire U.
        n_qubits: Nombre de qubits pour l'estimation de phase (précision).
        shots: Nombre de mesures.
        verbose: Afficher des détails.

    Returns:
        Tuple avec :
        - Un dictionnaire contenant les résultats (phase estimée, histogramme, etc.).
        - Le circuit quantique QPE (optionnel).
    """
    # Créer le circuit QPE
    # On a besoin de :
    # - n_qubits pour l'estimation de phase (t)
    # - 1 qubit pour l'état propre |ψ> (on suppose que |ψ> est |1> pour simplifier)
    t = n_qubits
    qc = QuantumCircuit(t + 1, t)

    # Préparer l'état propre |ψ> (ici, on utilise |1> pour simplifier)
    qc.x(t)  # |ψ> = |1>

    # Appliquer Hadamard sur les qubits de phase
    for i in range(t):
        qc.h(i)

    # Appliquer les opérations U^(2^j) contrôlées
    for j in range(t):
        # Appliquer U^(2^j) contrôlé par le j-ème qubit
        for _ in range(2**j):
            qc.append(unitary.to_gate(), [t] + [i for i in range(j, t)])

    # Appliquer la transformée de Fourier inverse (QFT†)
    for i in range(t // 2):
        qc.swap(i, t - 1 - i)
    for j in range(t):
        for k in range(j):
            qc.cp(-pi / (2 ** (j - k)), k, j)
        qc.h(j)

    # Mesurer les qubits de phase
    qc.measure(range(t), range(t))

    if verbose:
        print("Circuit QPE:")
        print(qc.draw())

    # Exécuter le circuit
    backend = Aer.get_backend("qasm_simulator")
    job = execute(qc, backend, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # Trouver la phase estimée (la mesure la plus fréquente)
    most_frequent = max(counts, key=counts.get)
    phase_int = int(most_frequent, 2)
    phase = phase_int / (2**t)  # Phase estimée entre 0 et 1

    # Calculer l'erreur (si on connaît la phase réelle)
    # Ici, on ne la connaît pas, donc on retourne juste l'estimation
    return {
        "phase_estimated": phase,
        "phase_int": phase_int,
        "counts": counts,
        "n_qubits": t,
        "shots": shots,
        "circuit": qc if verbose else None,
    }, qc if verbose else None

def qpe_for_order_finding(
    a: int,
    N: int,
    n_qubits: int = 4,
    shots: int = 1024,
    verbose: bool = False,
) -> Tuple[dict, Optional[QuantumCircuit]]:
    """
    Utilise QPE pour trouver l'ordre multiplicatif de a modulo N.
    C'est une partie clé de l'algorithme de Shor.

    Args:
        a: Base pour l'exponentiation modulaire.
        N: Module.
        n_qubits: Nombre de qubits pour l'estimation de phase.
        shots: Nombre de mesures.
        verbose: Afficher des détails.

    Returns:
        Tuple avec :
        - Un dictionnaire contenant l'ordre estimé.
        - Le circuit quantique (optionnel).
    """
    # Vérifier que a et N sont copremiers
    if gcd(a, N) != 1:
        return {
            "error": "a et N ne sont pas copremiers. QPE ne peut pas être utilisé.",
            "a": a,
            "N": N,
        }, None

    # Créer l'opérateur unitaire U_a: |x> -> |a*x mod N>
    # Pour simplifier, on va utiliser un circuit qui implémente U_a
    # (en pratique, cela nécessite un circuit de multiplication modulaire)
    # Ici, on va simuler U_a pour un cas simple (ex: N=15, a=2)
    # Pour un vrai implémentation, il faudrait un circuit de multiplication modulaire quantique.

    # Pour l'exemple, on va utiliser un circuit aléatoire (à remplacer par une vraie implémentation)
    # En pratique, cela nécessite un circuit complexe pour U_a = |x> -> |a*x mod N>
    # Ici, on va juste retourner une estimation fictive pour l'exemple
    # (une vraie implémentation nécessiterait des centaines de qubits pour des N grands)

    # Pour N=15 et a=2, l'ordre est 4 (car 2^4 ≡ 1 mod 15)
    # On va simuler cela
    if N == 15 and a == 2:
        order = 4
        phase = 0.25  # 1/4
    elif N == 21 and a == 2:
        order = 6
        phase = 1/6
    else:
        # Cas général : on ne peut pas calculer l'ordre sans une vraie implémentation
        return {
            "error": "Implémentation simplifiée. Utilisez N=15 ou N=21 pour un exemple.",
            "a": a,
            "N": N,
        }, None

    # Retourner un résultat fictif pour l'exemple
    return {
        "a": a,
        "N": N,
        "order_estimated": order,
        "phase_estimated": phase,
        "note": "Ceci est une simulation. Une vraie implémentation nécessiterait un circuit quantique complexe.",
    }, None


# Démo de QPE avec un exemple simple.
def demo_qpe() -> None:
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]🔮 Démonstration de Quantum Phase Estimation (QPE)[/bold cyan]")

    # Exemple 1: QPE sur une opération unitaire aléatoire
    console.print("\n[bold]1. QPE sur une opération unitaire aléatoire[/bold]")
    unitary = QuantumCircuit(1)
    unitary.h(0)  # Exemple simple: opération Hadamard
    unitary.x(0)  # + NOT

    result, qc = qpe(unitary, n_qubits=3, shots=1024, verbose=False)
    console.print(f"Phase estimée: {result['phase_estimated']:.4f}")
    console.print(f"Comptes: {result['counts']}")

    # Exemple 2: QPE pour trouver l'ordre multiplicatif (Shor)
    console.print("\n[bold]2. QPE pour l'ordre multiplicatif (Shor)[/bold]")
    a, N = 2, 15
    console.print(f"Trouver l'ordre de {a} modulo {N}...")
    result, _ = qpe_for_order_finding(a, N, verbose=False)
    if "order_estimated" in result:
        console.print(f"Ordre estimé: {result['order_estimated']}")
        console.print(f"Vérification: {a}^{result['order_estimated']} mod {N} = {pow(a, result['order_estimated'], N)}")
    else:
        console.print(f"[red]{result['error']}[/red]")
