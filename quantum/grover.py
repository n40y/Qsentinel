from qiskit import QuantumCircuit
from qiskit_aer import  AerSimulator
from math import isqrt, pi


# Marque l'état en inversant sa phase
# target est une chaine binaire dans laquelle on va chercher l'état
def oracle(qc: QuantumCircuit, target: str) -> None:

    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)
    
    qc.h(len(target) - 1)
    qc.mcx(list(range(len(target) - 1)), len(target) - 1)
    qc.h(len(target) - 1)
    
    # Annule les X appliqués avant
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)


# Augmente la probabilité de la solution. On amplifie l'amplitude
def diffuser(qc: QuantumCircuit, n_qubits: int) -> None:
    
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    

# Algorithm de Grover.
# Cherche l'état de target dans un espace de 2 puissance n états
# Retourne les mesures et stats dans un dictionnaire
def grover(target: str, shots: int=1024) -> dict:
    n = len(target)
    
    # Formule optimale : π/4 * √(2^n), minimum 1
    n_iterations = max(1, round((pi / 4) * (2 ** (n / 2))))
    
    if n <= 3:
        n_iterations = 1
    
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    
    for _ in range(n_iterations):
        oracle(qc, target)
        diffuser(qc, n)
        
    # mesure finale
    qc.measure(range(n), range(n))
    
    # simulation locale
    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    
    # Tri par fréquence décroissante
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


    
# Fonction appelée par main.py
# Impact de Grover sur le chiffrement AES.
def estimate_qunatum_time(results: dict) -> dict:
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
